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

def register_measurement(measurement):
    measurements[measurement.codeword] = measurement

def register_report(report):
    reports[report.codeword] = report