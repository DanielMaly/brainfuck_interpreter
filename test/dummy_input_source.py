__author__ = 'Daniel Maly'

from brainx.input_source import TextInputSource

class DummyInputSource(TextInputSource):
    def __init__(self, program, inp):
        super().__init__(program, inp)