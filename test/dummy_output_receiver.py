__author__ = 'Daniel Maly'

import brainx.output_receiver as OR

class DummyOutputReceiver(OR.OutputReceiver):
    def __init__(self):
        super().__init__()
        self.print_to_stdout = False



