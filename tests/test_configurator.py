"""Test script for chino configurator."""
import unittest
import numpy as np
import chino.configurator as cc
from chino.configurator import cfg
from chino.frozen_dict import FrozenDict


class TestCfg(unittest.TestCase):

    def setUp(self):
        cfg.SVM.C = 100.
        cfg.SVM.IMPL = 'lbfgs'
        cfg.NAME = 'default'
        cfg.freeze()

    def tearDown(self):
        cc.reset_cfg()

    def test_fields(self):
        self.assertIn('SVM', cfg)
        self.assertIn('NAME', cfg)
        self.assertEqual(cfg.NAME, 'default')
        self.assertEqual(cfg.SVM.C, 100.)
        self.assertEqual(cfg.SVM.IMPL, 'lbfgs')


class TestMerge(unittest.TestCase):

    def test_merge_from_dict(self):
        lcfg = FrozenDict()
        lcfg.RNG_SEED = 1234
        lcfg.NAME = 'default'
        lcfg.SVM.C = 100.
        lcfg.SVM.IMPL = 'lbfgs'
        lcfg.freeze()
        d = {'SVM': {'IMPL': 'generic'}}
        d2 = {'RNG_SEED': 'random'}
        cc._merge_dict_into_Dict(d, lcfg)
        self.assertEqual(lcfg.SVM.IMPL, 'generic')
        with self.assertRaises(Exception):
            cc._merge_dict_into_Dict(d2, lcfg)


if __name__ == "__main__":
    unittest.main()
