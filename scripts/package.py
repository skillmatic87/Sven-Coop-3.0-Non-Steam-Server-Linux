"""Allowlist the public release; never include an installed server or credentials."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def source_files():
    top=['README.md','LICENSE','VERSION','.gitignore','.gitattributes','Configure-Server.html','Setup-Linux.sh','Start-Server.sh','Start-Panel.sh']
    files=[ROOT/n for n in top]
    for folder in ('scripts','plugins','tests','docs'):
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ('.py','.sma','.md','.txt','.yml') and '__pycache__' not in p.parts and p.name!='BUILD-STATUS.md')
    return sorted(set(files))
def main():
    components=ROOT/'components';manifest=json.loads((components/'manifest.json').read_text())
    inputs=[components/n for n in manifest['files']]+[components/'manifest.json']
    for p in inputs:
        if p.name in manifest['files']:
            with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
            if sha!=manifest['files'][p.name]:raise ValueError('Component checksum mismatch: '+p.name)
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    path=dist/f"Sven-Coop-3.0-Linux-Mint-{manifest['version']}.zip"
    with zipfile.ZipFile(path,'w',zipfile.ZIP_STORED) as z:
        for p in source_files()+inputs:
            relative=p.relative_to(ROOT).as_posix()
            if '.local.' in relative or relative.startswith(('build/','SvenServer-Linux/')):raise ValueError('Private path in package')
            z.write(p,'Sven-Coop-3.0-Server-Linux/'+relative)
    with zipfile.ZipFile(path) as z:
        if z.testzip():raise ValueError('Release ZIP integrity failure')
    with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    path.with_suffix('.zip.sha256').write_text(f'{sha}  {path.name}\n')
    print(f'{path.name}: {path.stat().st_size} bytes; SHA-256 {sha}')
if __name__=='__main__':main()
