"""Build offline release inputs on Windows from original installed Sven 3.0 files."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, tarfile, zipfile
ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parent
def sha(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def pack_tree(source,target,include=lambda p:True):
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(source.rglob('*')):
            if p.is_file() and include(p): z.write(p,p.relative_to(source).as_posix())
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--sven',type=Path);ap.add_argument('--check',action='store_true');ap.add_argument('--package',action='store_true'); a=ap.parse_args()
    if a.check or a.package:
        subprocess.run([__import__('sys').executable,str(ROOT/'scripts'/('check.py' if a.check else 'package.py'))],check=True);return
    if not a.sven:ap.error('--sven is required for component assembly')
    research=WORKSPACE/'downloads/research'
    original=a.sven/'SvenCoop'
    if 'version "3.0"' not in (original/'liblist.gam').read_text(): raise ValueError('Expected Sven 3.0')
    out=ROOT/'components'; out.mkdir(exist_ok=True)
    shutil.copy2(research/'hlserver4110.exe',out/'hlserver4110.exe')
    shutil.copy2(WORKSPACE/'runtime/sven-wise-linux.zip',out/'wise-linux.zip')
    shutil.copy2(research/'hlds4110-unpacked/TEMP/EULAFILE',out/'HLDS-LICENSE.txt')
    pack_tree(original,out/'svencoop.zip',lambda p: p.name not in ('uninstal.log',))
    stage=ROOT/'build/plugins'; stage.mkdir(parents=True,exist_ok=True)
    shutil.copytree(research/'amxx181/addons',stage/'addons',dirs_exist_ok=True)
    with tarfile.open(research/'metamod-p-v1.21p109-win32.tar.xz') as z: z.extractall(stage,filter='data')
    compiler=research/'amxx181/addons/amxmodx/scripting'
    sources=list((ROOT/'plugins').glob('*.sma'))+[research/'sank/HL1_SankSounds-master/sank_sounds.sma']
    for src in sources:
        dest=stage/'addons/amxmodx/plugins'/src.with_suffix('.amxx').name
        subprocess.run([str(compiler/'amxxpc.exe'),str(src),'-i'+str(compiler/'include'),'-o'+str(dest)],check=True,cwd=compiler)
        if not dest.is_file(): raise RuntimeError('Missing compiled plugin')
        shutil.copy2(src,stage/'addons/amxmodx/scripting'/src.name)
    with zipfile.ZipFile(research/'statsme-soundpack.zip') as z:z.extractall(stage)
    shutil.copytree(WORKSPACE/'content/files/cstrike/sound/lan',stage/'sound/lan',dirs_exist_ok=True)
    sounds=sorted(p for p in (stage/'sound').rglob('*.wav'))
    cfg='SND_MAX; 20\nSND_MAX_DUR; 180.0\nSND_WARN; 17\nSND_JOIN; sound/lan/welcome.wav\nSND_EXIT;\nSND_DELAY; 10.0\nSND_MODE; 15\nSND_OBEY_DUR; 7\nEXACT_MATCH; 1\nADMINS_ONLY; 0\nDISPLAY_KEYWORDS; 1\nFREEZE_TIME_CON; 0\n'
    cfg+=''.join(p.stem+'; '+p.relative_to(stage).as_posix()+'\n' for p in sounds if p.stem!='welcome')
    (stage/'addons/amxmodx/configs/SND-LIST.CFG').write_text(cfg)
    notices=stage/'_notices';notices.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'docs/THIRD-PARTY.md',notices/'THIRD-PARTY.md')
    pack_tree(stage,out/'plugins.zip',lambda p:p.name!='CS-COMPONENT-SOURCES.md')
    with zipfile.ZipFile(out/'sources.zip','w',zipfile.ZIP_STORED) as z:
        for p in [WORKSPACE/'runtime/sven-amxx-source.zip',WORKSPACE/'runtime/sven-metamod-source.zip',research/'sank-pinned.zip']:
            z.write(p,p.name)
    names=['hlserver4110.exe','wise-linux.zip','svencoop.zip','plugins.zip','HLDS-LICENSE.txt','sources.zip']
    manifest={'schema':1,'version':(ROOT/'VERSION').read_text().strip(),'files':{n:sha(out/n) for n in names},'source':{'svenInstallerSHA256':'410d56668a63e57a03a58a6668c9466dacf99eeeabfe2f76955c1e2c9c0c7f1c','hldsInstallerSHA256':'178fdf8a3d43ab91063ccb83be05be0457c98db348fc28eba6b9c9ea4e5dc849'},'engine':{n:sha(research/'hlds4110-unpacked/MAINDIR'/n) for n in ('hlds.exe','swds.dll')}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
