#!/usr/bin/env python3

class Measurement(object):
    def __init__(self, codeword, handler_class, **kwargs):
        self.codeword = codeword
        self.handler_class = handler_class

measurements = dict()

def register_measurement(measurement):
    measurements[measurement.codeword] = measurement

