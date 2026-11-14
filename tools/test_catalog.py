import contextlib, io, os, pathlib, sqlite3, tempfile, unittest, csv
from build_catalog import build
class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.old=os.getcwd();os.chdir(self.tmp.name)
        self.csv=pathlib.Path(self.tmp.name)/'input.csv';os.environ['AIFA_CSV']=str(self.csv)
    def tearDown(self):
        os.chdir(self.old);os.environ.pop('AIFA_CSV',None);self.tmp.cleanup()
    def test_roundtrip(self):
        with self.csv.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f,delimiter=';');w.writerow(['CODICE_AIC','DENOMINAZIONE','DESCRIZIONE'])
            for i in range(1200):w.writerow([str(i),'TEST NON REALE','Test; unità'])
        with contextlib.redirect_stdout(io.StringIO()):build()
        with sqlite3.connect('app/src/main/assets/catalog.db') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM drugs').fetchone()[0],1200)
            self.assertEqual(db.execute('SELECT aic,description FROM drugs ORDER BY aic LIMIT 1').fetchone(),('000000000','Test; unità'))
    def test_lfs_rejected(self):
        self.csv.write_bytes(b'version https://git-lfs.github.com/spec/v1\n'+b'x'*2000)
        with self.assertRaises(RuntimeError):build()
    def test_wrong_schema_rejected(self):
        self.csv.write_text('WRONG;HEADER\n'+'abc;def\n'*1000)
        with self.assertRaises(RuntimeError):build()
if __name__=='__main__':unittest.main()
