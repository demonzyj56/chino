import unittest
from chino.frozen_dict import FrozenDict


class TestFrozenDict(unittest.TestCase):

    def test_setattr(self):
        fd = FrozenDict()
        fd.SVM.C = 100.
        fd.SVM.IMPL = 'lbfgs'
        fd.NAME = 'frozen_dict'
        self.assertTrue(hasattr(fd, 'NAME'))
        self.assertTrue(hasattr(fd, 'SVM'))
        self.assertIsInstance(fd.SVM, FrozenDict)
        self.assertEqual(fd.SVM.C, 100.)
        self.assertEqual(fd.SVM.IMPL, 'lbfgs')

    def test_freeze(self):
        fd = FrozenDict()
        fd.SVM.C = 100.
        fd.SVM.IMPL = 'lbfgs'
        fd.freeze()
        self.assertTrue(fd.is_frozen())
        with self.assertRaises(AttributeError):
            _ = fd.NAME
        with self.assertRaises(KeyError):
            fd.NAME = 'oooops'
        with self.assertRaises(KeyError):
            fd.SVM = 'Not SVM Options at all'


if __name__ == "__main__":
    unittest.main()
