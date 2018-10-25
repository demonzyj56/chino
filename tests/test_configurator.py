"""Test script for chino configurator."""
import unittest
import numpy as np
import chino.configurator as cc
from chino.frozen_dict import FrozenDict


class TestCfg(unittest.TestCase):

    def setUp(self):
        self.cfg = FrozenDict()
        self.cfg.SVM.C = 100.
        self.cfg.SVM.IMPL = 'lbfgs'
        self.cfg.NAME = 'default'
        self.cfg.freeze()

    def test_fields(self):
        self.assertIn('SVM', self.cfg)
        self.assertIn('NAME', self.cfg)
        self.assertEqual(self.cfg.NAME, 'default')
        self.assertEqual(self.cfg.SVM.C, 100.)
        self.assertEqual(self.cfg.SVM.IMPL, 'lbfgs')


class TestMerge(unittest.TestCase):

    def test_merge_from_dict(self):
        lcfg = FrozenDict()
        lcfg.RNG_SEED = 1234
        lcfg.NAME = 'default'
        lcfg.SVM.C = 100.
        lcfg.SVM.IMPL = 'lbfgs'
        lcfg.IMG_MEAN = np.random.rand(3)
        lcfg.freeze()
        d = {'SVM': {'IMPL': 'generic'}, 'IMG_MEAN': [1.2, 2.3, 3.4]}
        d2 = {'RNG_SEED': 'random'}
        cc._merge_dict_into_Dict(d, lcfg)
        self.assertEqual(lcfg.SVM.IMPL, 'generic')
        self.assertIsInstance(lcfg.IMG_MEAN, np.ndarray)
        self.assertTrue(np.allclose(lcfg.IMG_MEAN,
                                    np.array([1.2, 2.3, 3.4])))
        with self.assertRaises(Exception):
            cc._merge_dict_into_Dict(d2, lcfg)


class TestCfgParser(unittest.TestCase):

    def setUp(self):
        self.cfg = FrozenDict()
        self.cfg.SVM.ENABLED = True
        self.cfg.SVM.C = 100.
        self.cfg.SVM.IMPL = 'lbfgs'
        self.cfg.NAME = 'default'
        self.cfg.RNG_SEED = 9527
        self.cfg.IMG_SIZE = [224, 224, 3]
        self.cfg.IMG_MEAN = np.random.rand(3)
        self.cfg.freeze()

    def test_parse_args(self):
        parser = cc.cfg_parser(self.cfg)
        args = parser.parse_args("""
            --SVM.ENABLED False --SVM.C 1000.
            --SVM.IMPL generic --NAME TestParser --IMG_SIZE 256 256 1
            --IMG_MEAN 1.2 2.3 3.4
        """.split())
        cc.merge_from_parser_args(args, self.cfg)
        self.assertFalse(self.cfg.SVM.ENABLED)
        self.assertEqual(self.cfg.SVM.C, 1000.)
        self.assertEqual(self.cfg.SVM.IMPL, 'generic')
        self.assertEqual(self.cfg.NAME, 'TestParser')
        self.assertEqual(self.cfg.RNG_SEED, 9527)
        self.assertSequenceEqual(self.cfg.IMG_SIZE, [256, 256, 1])
        self.assertIsInstance(self.cfg.IMG_MEAN, np.ndarray)
        self.assertTrue(np.allclose(self.cfg.IMG_MEAN,
                                    np.array([1.2, 2.3, 3.4])))


if __name__ == "__main__":
    unittest.main()
