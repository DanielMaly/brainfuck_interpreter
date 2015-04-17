__author__ = 'Daniel Maly'

from input_source import InputSource


class DummyInputSource(InputSource):
    def __init__(self, program, inp):
        super().__init__(program, inp)