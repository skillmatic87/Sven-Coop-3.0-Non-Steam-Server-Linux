from pathlib import Path
import ast,shutil,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
for p in list((ROOT/'scripts').glob('*.py'))+list((ROOT/'tests').glob('*.py')):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
bash=Path('C:/Program Files/Git/bin/bash.exe') if sys.platform=='win32' else shutil.which('bash')
if bash:
    for p in ROOT.glob('*.sh'):subprocess.run([str(bash),'-n',str(p)],check=True)
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():sys.exit(1)
print('Python syntax, launcher syntax and package tests passed.')
