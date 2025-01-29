import unittest
import sys
import shutil
import os
from multiprocessing import Process

sys.path.append('../')
from watcher.watcher import Watcher, get_files
from packer.packer import Packer



class TestCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_file = '../config.toml'
        cls.trg = 'test_watchee/'
        prev = os.path.abspath('../')

        if os.path.exists(cls.trg):
            shutil.rmtree(cls.trg)
        shutil.copytree(src=prev, dst=cls.trg, ignore=shutil.ignore_patterns('tests'))

        cls.packer = Packer(config_file, cls.trg, b'terrible_password')
        cls.watcher = Watcher(config_file, cls.trg)

        #make _test_watchee()
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.trg)
        if os.path.isdir('packer/'):
            shutil.rmtree('packer/')

    def test_watching(self):
        change = os.path.join(self.trg, 'blabla.txt')
        with open(change, 'w') as f:
            f.write('blablablah')
        are_diff = [self.watcher.update(get_files(self.watcher.watchee))]
        with open(change, 'a') as f:
            f.write('hehe im back')
        are_diff.append(self.watcher.update(get_files(self.watcher.watchee)))

        self.assertTrue(are_diff[0] and are_diff[1])

    def test_packing(self):
        flist = get_files(self.trg)
        data = self.packer.make_package()

        self.packer.depackage()

        new_flist = get_files(os.path.join(self.packer.restore_dir, self.trg))
        self.assertTrue(len(new_flist) == len(flist))



if __name__ == '__main__':
    unittest.main()







