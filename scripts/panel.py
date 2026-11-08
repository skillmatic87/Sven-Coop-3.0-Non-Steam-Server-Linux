"""Loopback-only operator panel with a per-session capability token."""
import atexit, hashlib, http.server, ipaddress, json, os, re, secrets, sys, threading, webbrowser,subprocess
from pathlib import Path
import control
ROOT=Path(__file__).resolve().parents[1]
TOKEN=secrets.token_urlsafe(32)
controller=None
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,code,data,kind='application/json'):
        data=data if isinstance(data,bytes) else json.dumps(data).encode()
        self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.end_headers();self.wfile.write(data)
    def authorized(self):
        expected=f'127.0.0.1:{self.server.server_port}'
        return self.headers.get('Host')==expected and secrets.compare_digest(self.headers.get('X-Panel-Token',''),TOKEN) and self.headers.get('Origin',f'http://{expected}')==f'http://{expected}'
    def do_GET(self):
        if self.path=='/':return self.reply(200,(ROOT/'Configure-Server.html').read_bytes(),'text/html; charset=utf-8')
        if not self.authorized():return self.reply(403,{'error':'Access denied'})
        if self.path!='/api/state':return self.reply(404,{'error':'Not found'})
        try:
            game=controller.server/'svencoop'
            self.reply(200,{'running':controller.running(),'settings':controller.settings(),'maps':sorted(p.stem for p in (game/'maps').glob('*.bsp')),'rotation':(game/'addons/amxmodx/configs/sven_maps.ini').read_text(),'sounds':(game/'addons/amxmodx/configs/SND-LIST.CFG').read_text(),'motd':(game/'motd.txt').read_text()})
        except (OSError,ValueError) as e:self.reply(400,{'error':str(e)})
    def do_POST(self):
        if not self.authorized():return self.reply(403,{'error':'Access denied'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<0 or length>65536:raise ValueError('Request too large')
            data=json.loads(self.rfile.read(length) or b'{}')
            if self.path=='/api/start':controller.start()
            elif self.path=='/api/stop':controller.stop()
            elif self.path=='/api/save':
                with controller.editing():
                    if controller.running():raise ValueError('Stop server before saving')
                    rotation=data['rotation'].split()
                    valid={p.stem for p in (controller.server/'svencoop/maps').glob('*.bsp')}
                    if not rotation or any(m not in valid or not re.fullmatch(r'[a-z0-9_]{1,31}',m) for m in rotation):raise ValueError('Invalid map rotation')
                    if 'stadium3' in rotation:raise ValueError('Stadium3 requires Steam; exclude it from WON rotation')
                    if not isinstance(data['motd'],str) or len(data['motd'])>4096 or not data['motd'].isascii():raise ValueError('MOTD must be ASCII, max 4096 characters')
                    # Validate all fields before writing any file.
                    control.setup.validate(data['settings'])
                    for p in ('settings.json','svencoop/server.cfg','svencoop/motd.txt','svencoop/mapcycle.txt','svencoop/addons/amxmodx/configs/sven_maps.ini'):
                        path=controller.server/p;backup=path.with_name(path.name+'.panel-backup');backup.write_bytes(path.read_bytes());backup.chmod(0o600)
                    control.setup.configure(controller.server,data['settings'],json.loads((controller.server/'credentials.local.json').read_text()))
                    control.setup.write(controller.server/'svencoop/mapcycle.txt','\n'.join(rotation)+'\n')
                    control.setup.write(controller.server/'svencoop/addons/amxmodx/configs/sven_maps.ini','\n'.join(rotation)+'\n')
                    control.setup.write(controller.server/'svencoop/motd.txt',data['motd'])
            elif self.path=='/api/profile':
                with controller.editing():
                    label=data['label']
                    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,31}',label):raise ValueError('Invalid profile name')
                    p=controller.server/'svencoop/addons/amxmodx/configs/sven_profiles.ini'
                    lines=p.read_text().splitlines()
                    if len(lines)>=128 or any('"'+label+'"' in line for line in lines):raise ValueError('Name exists or 128-profile limit reached')
                    token=secrets.token_hex(12);line=f'"{hashlib.md5(token.encode()).hexdigest()}" "{label}"\n'
                    with p.open('a') as f:f.write(line)
                    p.chmod(0o600)
                return self.reply(200,{'ok':True,'clientCommand':f'setinfo _scprofile "{token}"'})
            else:return self.reply(404,{'error':'Not found'})
            self.reply(200,{'ok':True})
        except (OSError,ValueError,KeyError,TypeError,RuntimeError,subprocess.SubprocessError) as e:self.reply(400,{'error':str(e)})
def main():
    global controller
    if sys.platform!='linux' or os.geteuid()==0:raise ValueError('Run on Mint as a regular user')
    os.umask(0o077);controller=control.Controller(control.server_path())
    server=http.server.ThreadingHTTPServer(('127.0.0.1',8766),Handler)
    url=f'http://127.0.0.1:8766/#{TOKEN}'
    print('Local panel: '+url,flush=True);atexit.register(controller.stop)
    if '--no-browser' not in sys.argv:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();controller.stop()
if __name__=='__main__':main()
