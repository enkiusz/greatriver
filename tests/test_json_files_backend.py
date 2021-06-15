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
from secondlife.plugins.json_files_backend import JsonFiles

import tempfile
import os

class TestJsonFilesBackend(unittest.TestCase):
    def setUp(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self.dsn = tempdir
            self.backend = JsonFiles(dsn=self.dsn)
            self.backend.init()

    def test_create(self):
        print('dsn', self.dsn)

        infoset = self.backend.create(id='FAKE~1')

        self.assertEqual(infoset.fetch('.id'), 'FAKE~1')
        self.assertEqual(infoset.fetch('.path'), None)
        first_event = infoset.fetch('.log')[0]

        # We don't want to fiddle with checking time
        self.assertIn('ts', first_event)
        first_event.pop('ts')

        self.assertEqual(first_event, {"type": "lifecycle", "event": "entry-created"})

    def test_put(self):
        pass

if __name__ == '__main__':
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    load_plugins()
    
    unittest.main()
