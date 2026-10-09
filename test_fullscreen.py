import unittest,sys,tempfile,runpy
from unittest.mock import patch
from pathlib import Path
from fullscreen_cli import safe,UI
class Fake:
 def __init__(self,keys):self.keys=iter(keys)
 def getmaxyx(self):return 24,80
 def erase(self):pass
 def addnstr(self,*a):pass
 def refresh(self):pass
 def get_wch(self):return next(self.keys)
class Tests(unittest.TestCase):
 def test_safe(self):self.assertNotIn('\x1b',safe('a\x1b[31m'))
 def test_input(self):self.assertEqual(UI(Fake(['a','b','\x7f','c','\n']),'test').input('x'),'ac')
 def test_cancel(self):
  with self.assertRaises(KeyboardInterrupt):UI(Fake(['\x03']),'test').input()
 def test_limit(self):
  u=UI(Fake([]),'x');u.add('\n'.join(map(str,range(4000))));self.assertEqual(len(u.lines),3000)
if __name__=='__main__':unittest.main()
