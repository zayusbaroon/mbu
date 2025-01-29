import unittest
import sys

sys.path.append('../')
from watcher.watcher import *



class TestAux(unittest.TestCase):
    def test_get_files(self):
        directory = 'test_watchee/'
        files = get_files(directory)
        self.assertTrue(len(files) > 1)


