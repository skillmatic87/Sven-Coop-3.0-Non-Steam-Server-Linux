from pathlib import Path
import hashlib,http.client,http.server,json,sys,tempfile,threading,unittest,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import setup,panel
class Tests(unittest.TestCase):
    def test_reject_config_injection_and_invalid_slots(self):
        for key,value in [('name','Bad";quit'),('map','../escape'),('slots',True),('port',70000),('bind','bad-ip')]:
            with self.subTest(key=key),self.assertRaises(ValueError):setup.validate(dict(setup.DEFAULTS,**{key:value}))
    def test_zip_traversal_does_not_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);archive=root/'bad.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('../escaped','bad')
            with self.assertRaises(ValueError):setup.extract(archive,root/'target')
            self.assertFalse((root/'escaped').exists())
    def test_existing_server_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'keep').write_text('preserve')
            with self.assertRaises(FileExistsError):setup.assemble(root,root/'missing',setup.DEFAULTS)
            self.assertEqual((root/'keep').read_text(),'preserve')
    def test_checksum_failure_precedes_installation(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);components=root/'components';components.mkdir()
            names=['hlserver4110.exe','wise-linux.zip','svencoop.zip','plugins.zip','HLDS-LICENSE.txt','sources.zip']
            for n in names:(components/n).write_bytes(b'actual')
            (components/'manifest.json').write_text(json.dumps({'files':{n:'0'*64 for n in names}}))
            with self.assertRaises(ValueError):setup.assemble(root/'server',components,setup.DEFAULTS)
            self.assertFalse((root/'server').exists())
    def test_panel_requires_capability_and_same_origin(self):
        class Fake:
            started=0
            def start(self):self.started+=1
        fake=Fake();previous=panel.controller;panel.controller=fake
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),panel.Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            port=server.server_port
            for headers in ({},{'X-Panel-Token':panel.TOKEN,'Origin':'https://attacker.invalid'},{'X-Panel-Token':panel.TOKEN,'Host':'attacker.invalid'}):
                c=http.client.HTTPConnection('127.0.0.1',port);c.request('POST','/api/start',body='{}',headers=headers);r=c.getresponse();self.assertEqual(r.status,403);r.read();c.close()
            self.assertEqual(fake.started,0)
            c=http.client.HTTPConnection('127.0.0.1',port);c.request('POST','/api/start',body='{}',headers={'X-Panel-Token':panel.TOKEN});r=c.getresponse();self.assertEqual(r.status,200);r.read();c.close();self.assertEqual(fake.started,1)
        finally:server.shutdown();server.server_close();panel.controller=previous
if __name__=='__main__':unittest.main()
