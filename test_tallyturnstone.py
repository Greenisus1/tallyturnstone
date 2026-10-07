import csv,io,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
import tallyturnstone as t
class TallyTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.p=Path(self.temp.name);self.db=t.connect(self.p/'db.sqlite3');self.ident=t.create(self.db,'Demo')
    def tearDown(self):self.db.close();self.temp.cleanup()
    def test_new_zero(self):self.assertEqual(t.get(self.db,self.ident)['value'],0)
    def test_add(self):self.assertEqual(t.adjust(self.db,self.ident,3),3)
    def test_subtract(self):t.adjust(self.db,self.ident,3);self.assertEqual(t.adjust(self.db,self.ident,-2),1)
    def test_lower_bound(self):
        with self.assertRaises(ValueError):t.adjust(self.db,self.ident,-1)
        self.assertEqual(t.history(self.db,self.ident),[])
    def test_upper_bound(self):
        t.adjust(self.db,self.ident,t.LIMIT)
        with self.assertRaises(ValueError):t.adjust(self.db,self.ident,1)
        self.assertEqual(t.get(self.db,self.ident)['value'],t.LIMIT)
    def test_invalid_delta(self):
        for delta in (0,True,1.5,t.LIMIT+1):
            with self.assertRaises(ValueError):t.adjust(self.db,self.ident,delta)
    def test_undo(self):t.adjust(self.db,self.ident,4);self.assertTrue(t.undo(self.db,self.ident));self.assertEqual(t.get(self.db,self.ident)['value'],0);self.assertEqual(t.history(self.db,self.ident)[0]['undone'],1)
    def test_undo_lifo(self):t.adjust(self.db,self.ident,4);t.adjust(self.db,self.ident,-1);t.undo(self.db,self.ident);self.assertEqual(t.get(self.db,self.ident)['value'],4);t.undo(self.db,self.ident);self.assertEqual(t.get(self.db,self.ident)['value'],0)
    def test_no_undo(self):self.assertFalse(t.undo(self.db,self.ident))
    def test_independent(self):other=t.create(self.db,'Other');t.adjust(self.db,self.ident,1);t.adjust(self.db,other,2);t.undo(self.db,self.ident);self.assertEqual(t.get(self.db,other)['value'],2)
    def test_duplicate(self):
        with self.assertRaises(sqlite3.IntegrityError):t.create(self.db,'Demo')
    def test_unknown(self):
        with self.assertRaises(ValueError):t.adjust(self.db,999,1)
    def test_sql_literal(self):ident=t.create(self.db,"x'; DROP TABLE counters;--");self.assertIn('DROP TABLE',t.get(self.db,ident)['name'])
    def test_csv_safe(self):ident=t.create(self.db,'=formula');p=self.p/'out.csv';t.export(self.db,p);rows=list(csv.reader(io.StringIO(p.read_text())));self.assertEqual(rows[-1][1],"'=formula")
    def test_no_overwrite(self):
        p=self.p/'safe';p.write_text('safe')
        with self.assertRaises(FileExistsError):t.export(self.db,p)
    def test_persistence(self):t.adjust(self.db,self.ident,3);self.db.close();self.db=t.connect(self.p/'db.sqlite3');self.assertEqual(t.get(self.db,self.ident)['value'],3)
    def test_cli(self):r=subprocess.run([sys.executable,'tallyturnstone.py','--db',str(self.p/'cli.sqlite3')],input='2\nSession\n3\n1\n5\n1\n0\n',capture_output=True,text=True);self.assertEqual(r.returncode,0);self.assertIn('New count: 5',r.stdout)
if __name__=='__main__':unittest.main()
