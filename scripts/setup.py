"""Offline assembly. Original engines and mod resources remain separate inputs."""
from pathlib import Path, PurePosixPath
import argparse, getpass, hashlib, ipaddress, json, os, re, secrets, shutil, socket, stat, subprocess, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
DEFAULTS={'name':'Sven Co-op 3.0 LAN','slots':12,'port':27016,'map':'sandstone','minutes':30,'skill':1,'bind':'0.0.0.0','admin':'Admin'}
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='ascii',newline='\n');path.chmod(0o600)
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def validate(s):
    s=dict(s)
    if set(s)!=set(DEFAULTS):raise ValueError('Unexpected settings fields')
    for key,low,high in [('slots',2,32),('port',1024,65535),('minutes',6,180),('skill',1,3)]:
        if type(s[key]) is not int or not low<=s[key]<=high:raise ValueError(f'Invalid {key}')
    for key,limit in [('name',63),('admin',31)]:
        if not isinstance(s[key],str) or not re.fullmatch(r'[A-Za-z0-9 _.-]{1,'+str(limit)+'}',s[key]):raise ValueError(f'Invalid {key}: use ASCII letters, numbers, spaces, dots, dashes or underscores')
    if not re.fullmatch(r'[a-z0-9_]{1,31}',s['map']):raise ValueError('Invalid map')
    ipaddress.IPv4Address(s['bind'])
    return s
def extract(path,dest):
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            p=PurePosixPath(info.filename.replace('\\','/'))
            if p.is_absolute() or any(v in ('.','..') or ':' in v for v in p.parts) or stat.S_ISLNK(info.external_attr>>16):raise ValueError('Unsafe archive path')
            target=dest.joinpath(*p.parts)
            if info.is_dir(): target.mkdir(parents=True,exist_ok=True);continue
            target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(info) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
def configure(server,s,credentials):
    s=validate(s);game=server/'svencoop';amxx=game/'addons/amxmodx/configs'
    if not (game/'maps'/f"{s['map']}.bsp").is_file():raise ValueError('Start map not installed')
    write(game/'server.cfg',f'''hostname "{s['name']}"
rcon_password "{credentials['rcon']}"
sv_lan 1
deathmatch 1
coop 0
mp_allowmonsters 1
mp_friendlyfire 0
sv_cheats 0
sv_allowdownload 1
sv_allowupload 0
skill {s['skill']}
mp_timelimit 0
mp_fraglimit 0
mp_voteallow 0
log on
sc_map_minutes {s['minutes']}
''')
    write(amxx/'users.ini',f'"{s["admin"]}" "{credentials["amx"]}" "abcdefghijklmnopqrstu" "a"\n')
    write(server/'settings.json',json.dumps(s,indent=2)+'\n')
def assemble(server,components,s,engine_directory=None):
    s=validate(s)
    if server.exists() or server.is_symlink():raise FileExistsError('Destination exists; choose a new empty destination')
    manifest=json.loads((components/'manifest.json').read_text())
    if set(manifest['files'])!={'hlserver4110.exe','wise-linux.zip','svencoop.zip','plugins.zip','HLDS-LICENSE.txt','sources.zip'}:raise ValueError('Unexpected component list')
    for name,sha in manifest['files'].items():
        if digest(components/name)!=sha:raise ValueError(f'Checksum mismatch: {name}')
    server.mkdir(parents=True,mode=0o700);write(server/'.incomplete','Installation incomplete\n')
    if engine_directory is not None:
        shutil.copytree(engine_directory,server,dirs_exist_ok=True)
    else:
        work=server/'_setup';tools=work/'tools';tools.mkdir(parents=True)
        extract(components/'wise-linux.zip',tools)
        unpacker=tools/'WiseUnpacker'
        if not unpacker.is_file():raise ValueError('Missing Linux WiseUnpacker')
        unpacker.chmod(0o700)
        subprocess.run([str(unpacker),'-x','-o',str(work/'engine'),str(components/'hlserver4110.exe')],check=True,timeout=300)
        source=work/'engine/MAINDIR'
        if not (source/'hlds.exe').is_file():raise ValueError('Original HLDS extraction failed; see _setup')
        shutil.copytree(source,server,dirs_exist_ok=True)
    shutil.copy2(components/'HLDS-LICENSE.txt',server/'HLDS-LICENSE.txt')
    game=server/'svencoop';game.mkdir();extract(components/'svencoop.zip',game)
    extract(components/'plugins.zip',game)
    # Only this additional Sven runtime DLL belongs at engine root, never swds.dll.
    shutil.copyfile(game/'fmod.dll',server/'fmod.dll')
    for name,sha in manifest['engine'].items():
        if digest(server/name)!=sha:raise ValueError('Engine changed during assembly')
    for p in (server/'hlds.exe',server/'swds.dll',game/'dlls/hl.dll',game/'addons/metamod/dlls/metamod.dll'):
        if p.read_bytes()[:2]!=b'MZ':raise ValueError(f'Missing Windows binary: {p.name}')
    # The original WON selection script copies these variants. Apply those exact copies.
    for folder,target in [(game/'maps/won',game/'maps'),(game/'sound/scsentences/won',game/'sound')]:
        for p in folder.glob('*'):
            if p.is_file():shutil.copyfile(p,target/p.name)
    lib=(game/'liblist.gam').read_text();lib,n=re.subn(r'(?m)^gamedll\s+"[^"]+"','gamedll "addons/metamod/dlls/metamod.dll"',lib)
    if n!=1:raise ValueError('Unexpected liblist.gam')
    write(game/'liblist.gam',lib)
    amxx=game/'addons/amxmodx/configs'
    write(game/'addons/metamod/plugins.ini','win32 addons/amxmodx/dlls/amxmodx_mm.dll\n')
    plugins='admin admincmd adminhelp multilingual menufront cmdmenu plmenu mapsmenu pluginmenu adminchat antiflood adminvote pausecfg sven_stats sven_maps sank_sounds'.split()
    write(amxx/'plugins.ini',''.join(p+'.amxx\n' for p in plugins))
    write(amxx/'modules.ini','engine\nnvault\n')
    write(amxx/'amxx.cfg','amx_language en\namx_client_languages 0\namx_mode 1\n')
    candidates='sandstone osprey afrikakorps1 auspices extended rampage sc_another sc_greysnake1 toonrun1 vger zero'.split()
    candidates=[m for m in candidates if (game/'maps'/f'{m}.bsp').is_file()]
    write(game/'mapcycle.txt','\n'.join(candidates)+'\n');write(amxx/'sven_maps.ini','\n'.join(candidates)+'\n')
    # Sven's built-in votes must not race the AMXX vote system.
    write(game/'mapvote.cfg','// Package uses sven_maps.amxx; native vote configuration disabled.\n')
    creds={key:secrets.token_hex(16) for key in ('amx','rcon')}
    token=secrets.token_hex(12)
    write(amxx/'sven_profiles.ini',f'"{hashlib.md5(token.encode()).hexdigest()}" "Player1"\n')
    write(server/'credentials.local.json',json.dumps(creds)+'\n')
    write(server/'ADMIN.local.txt',f'Admin name: {s["admin"]}\nAMXX password: {creds["amx"]}\nRCON password: {creds["rcon"]}\n\nAMXX client console: setinfo _pw "{creds["amx"]}"\nUse amxmodmenu after connecting with the admin name.\n\nPlayer1 profile (separate from admin):\nsetinfo _scprofile "{token}"\nSave the profile line in the client autoexec.cfg. Do not share it.\nGuests receive session statistics only. Tokens are for a trusted LAN, not encrypted login.\n')
    configure(server,s,creds)
    write(game/'motd.txt','Sven Co-op 3.0 LAN\n/statsme  /rank  /top15\n/nominate mapname  /rtv  /nextmap\n/sounds lists chat sounds. Admins: amxmodmenu\nRanking measures co-op scoreboard points, not monster kills.\n')
    shutil.copy2(components/'manifest.json',server/'COMPONENTS.json')
    (server/'.incomplete').unlink()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination',type=Path,default=ROOT/'SvenServer-Linux');ap.add_argument('--defaults',action='store_true');ap.add_argument('--settings',type=Path);args=ap.parse_args()
    if sys.platform!='linux' or os.geteuid()==0:ap.error('Run as a regular Linux Mint user, without sudo')
    for name in ('wine','wineconsole','wineboot'):
        if not shutil.which(name):ap.error('Missing '+name+'; follow README dependency instructions')
    os.umask(0o077);s=DEFAULTS.copy()
    if args.settings:s.update(json.loads(args.settings.read_text()))
    elif not args.defaults:
        for key in DEFAULTS:
            value=input(f'{key} [{s[key]}]: ').strip()
            if value:s[key]=int(value) if type(s[key]) is int else value
    print((ROOT/'components/HLDS-LICENSE.txt').read_text(encoding='latin1'))
    if input('Accept the original HLDS license and install? [y/N]: ').strip().lower() not in ('y','yes','j','ja'):raise ValueError('License not accepted')
    server=args.destination.expanduser().absolute();assemble(server,ROOT/'components',s)
    write(ROOT/'server.local.json',json.dumps({'path':str(server)})+'\n')
    print(f'Installed: {server}\nPrivate credentials: {server}/ADMIN.local.txt\nStart: bash Start-Server.sh')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,subprocess.SubprocessError) as e:print(f'Setup stopped: {e}',file=sys.stderr);sys.exit(1)
