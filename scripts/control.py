"""Control only this installation's Wine prefix and child process."""
from pathlib import Path
import json, os, signal, socket, subprocess, sys, threading, time
from contextlib import contextmanager
import setup
ROOT=Path(__file__).resolve().parents[1]
def server_path():
    record=ROOT/'server.local.json'
    p=Path(json.loads(record.read_text())['path']) if record.exists() else ROOT/'SvenServer-Linux'
    p=p.resolve()
    if not (p/'COMPONENTS.json').is_file() or (p/'.incomplete').exists():raise ValueError('Run Setup-Linux.sh first')
    return p
def rcon(server,command):
    s=setup.validate(json.loads((server/'settings.json').read_text()))
    password=json.loads((server/'credentials.local.json').read_text())['rcon']
    address='127.0.0.1' if s['bind']=='0.0.0.0' else s['bind']
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.settimeout(1.5);sock.connect((address,s['port']))
        sock.send(b'\xff'*4+b'challenge rcon\x00');data=sock.recv(65535).decode('latin1')
        challenge=data.split('challenge rcon ')[1].split()[0].strip('\x00')
        if not challenge.lstrip('-').isdigit():raise ValueError('Invalid RCON challenge')
        sock.send(b'\xff'*4+f'rcon {challenge} "{password}" {command}\x00'.encode('ascii'))
        replies=[]
        for _ in range(30):
            try:replies.append(sock.recv(65535)[5:].decode('latin1').strip('\x00'))
            except socket.timeout:break
        return ''.join(replies)
class Controller:
    def __init__(self,server):
        self.server=server;self.process=None;self.guard=threading.RLock();self.lockfile=None
        self.prefix=server/'wineprefix'
        if self.prefix.is_symlink():raise ValueError('Wine prefix must not be a symlink')
        self.env=dict(os.environ,WINEPREFIX=str(self.prefix),WINEARCH='win32',WINEDEBUG='-all')
    def running(self):return self.process is not None and self.process.poll() is None
    def start(self):
        import fcntl,pty
        with self.guard:
            if self.running():raise ValueError('Server already running')
            if self.lockfile:self.lockfile.close()
            self.lockfile=(self.server/'.run.lock').open('a')
            try:fcntl.flock(self.lockfile,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:self.lockfile.close();self.lockfile=None;raise ValueError('Another launcher owns this server')
            s=setup.validate(json.loads((self.server/'settings.json').read_text()))
            try:
                if not (self.prefix/'system.reg').exists():subprocess.run(['wineboot','-u'],env=self.env,check=True,timeout=120)
                master,slave=pty.openpty()
                try:self.process=subprocess.Popen(['wineconsole','--backend=curses','hlds.exe','-console','-game','svencoop','-nomaster','-insecure','-noipx','-port',str(s['port']),'+ip',s['bind'],'+sv_lan','1','+maxplayers',str(s['slots']),'+map',s['map']],cwd=self.server,env=self.env,stdin=slave,stdout=slave,stderr=slave,start_new_session=True)
                finally:os.close(slave)
                threading.Thread(target=self.read_console,args=(master,),daemon=True).start()
            except Exception:
                self.lockfile.close();self.lockfile=None;raise
    def read_console(self,fd):
        try:
            with (self.server/'console.log').open('ab') as log:
                while True:
                    try:data=os.read(fd,8192)
                    except OSError:break
                    if not data:break
                    log.write(data);log.flush()
        finally:os.close(fd)
    def stop(self):
        with self.guard:
            if self.running():
                try:rcon(self.server,'quit');self.process.wait(timeout=10)
                except (OSError,ValueError,IndexError,subprocess.TimeoutExpired):
                    if self.running():os.killpg(self.process.pid,signal.SIGTERM)
                try:self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(self.process.pid,signal.SIGKILL);self.process.wait(timeout=5)
            if self.lockfile:
                # Dedicated per-installation prefix: never kill the user's other Wine apps.
                subprocess.run(['wineserver','-k'],env=self.env,timeout=10,check=False)
                self.lockfile.close();self.lockfile=None
    def settings(self):return setup.validate(json.loads((self.server/'settings.json').read_text()))
    @contextmanager
    def editing(self):
        import fcntl
        with self.guard:
            if self.running():raise ValueError('Stop server before saving')
            with (self.server/'.run.lock').open('a') as lock:
                try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:raise ValueError('Another launcher owns this server')
                yield
    def save(self,s):
        with self.editing():
            setup.configure(self.server,s,json.loads((self.server/'credentials.local.json').read_text()))
def main():
    if sys.platform!='linux' or os.geteuid()==0:raise ValueError('Run on Linux as a regular user')
    c=Controller(server_path())
    try:
        c.start();print('Server starting; log: '+str(c.server/'console.log'),flush=True)
        while c.running():time.sleep(1)
        if c.process.returncode:raise RuntimeError(f'Wine console exited: {c.process.returncode}; inspect console.log')
    except KeyboardInterrupt:pass
    finally:c.stop()
if __name__=='__main__':main()
