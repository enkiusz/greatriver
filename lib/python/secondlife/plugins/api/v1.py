#!/usr/bin/env python3

class Measurement(object):
    def __init__(self, codeword, handler_class, **kwargs):
        self.codeword = codeword
        self.handler_class = handler_class

class Report(object):
    def __init__(self, codeword, handler_class, **kwargs):
        self.codeword = codeword
        self.handler_class = handler_class
        self.default_enable = kwargs.get('default_enable', False)

measurements = dict()
reports = dict()
state_vars = dict()
celldb_backends = dict()
infoset_transforms = dict()

def register_measurement(measurement):
    measurements[measurement.codeword] = measurement

def register_report(report):
    reports[report.codeword] = report

def register_state_var(path, handler_class):
    state_vars[path] = handler_class

def register_celldb_backend(codeword, backend_class):
    celldb_backends[codeword] = backend_class

def register_infoset_transform(codeword, transform_class):
    infoset_transform[codeword] = transform_class
