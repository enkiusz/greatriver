#!/usr/bin/env python3

# Allow module load from lib/python in main repo
import sys
from pathlib import Path
currentdir = Path(__file__).resolve(strict=True).parent
libdir = currentdir.parent.joinpath('lib/python')
sys.path.append(str(libdir))

import logging
import structlog
import unittest

from secondlife.infoset import Infoset


class TestInfoset(unittest.TestCase):

    def test_put_fetch(self):
        infoset = Infoset()

        infoset.put('.value1', 42)
        infoset.put('.dict.key', 'value')

        self.assertEqual(infoset.fetch('.dict'), {'key': 'value'})
        self.assertEqual(infoset.fetch('.dict.notexist', 'FAKE_VALUE'), 'FAKE_VALUE')

    def test_paths(self):

        infoset = Infoset()

        infoset.put('.item1.v1', 123)
        infoset.put('.item2', 999)

        self.assertEqual(infoset.paths(), ['.', '.item1', '.item1.v1', '.item2'])

    def test_dynamic_property(self):

        class DynamicProp1(object):
            def fetch(self, path, default=None):
                return 12

        class DynamicProp2(object):
            def __init__(self):
                self.d = dict(prop1='bb', prop2=12)

            def _find(self, path, mkpath=False):
                return self.d.get(path, 'FAKE_VALUE')

            def fetch(self, path):
                if path == '':
                    return self.d

                return self.d.get(path, 'FAKE_VALUE')

        d2 = DynamicProp2()

        infoset = Infoset()

        infoset.put('.dynamicprop1', DynamicProp1())
        infoset.put('.dynamicprop2', DynamicProp2())

        self.assertEqual(infoset.fetch('.dynamicprop1'), 12)
        self.assertEqual(infoset.fetch('.dynamicprop2'), d2.d)
        self.assertEqual(infoset.fetch('.dynamicprop2.prop1'), d2.d['prop1'])

        self.assertEqual(infoset.fetch('.dynamicprop2.notexist', 'FAKE_VALUE'), 'FAKE_VALUE')

    def test_embedded_infoset(self):

        infoset = Infoset()
        infoset1 = Infoset(dict(id=42))

        infoset.put('.embedded', infoset1)

        # self.assertEqual(infoset.fetch('.embedded'), dict(id=42))

        # infoset.put('.embedded.key', 'VALUE')
        # self.assertEqual(infoset.fetch('.embedded.key'), 'VALUE')

        # infoset.put('.embedded.key2', dict(second_id=112))
        # self.assertEqual(infoset.fetch('.embedded.key2')['second_id'], 112)

        infoset.put('.embedded.key3.inside', 'LOOK INSIDE')
        self.assertEqual(infoset.fetch('.embedded.key3.inside'), 'LOOK INSIDE')

    def test_internal_reference(self):

        infoset = Infoset()
        infoset.put('.log', [ dict(type='lifecycle') ])

        cell_log = infoset.fetch('.log')

        cell_log.append(dict(type='test-event'))

        assert(infoset.fetch('.log')[1]['type'] == 'test-event')


if __name__ == '__main__':
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    unittest.main()
