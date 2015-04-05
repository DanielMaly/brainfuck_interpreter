__author__ = 'Daniel Maly'


class DummyOutputReceiver:
    def __init__(self):
        self.output = []
        self.debug_info = None

    def put_char(self, char):
        self.output.append(char)

    def print_debug_info(self, debug_info):
        self.debug_info = debug_info