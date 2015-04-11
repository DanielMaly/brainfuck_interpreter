__author__ = 'Daniel Maly'

import unittest
from test.dummy_input_source import DummyInputSource
from test.dummy_output_receiver import DummyOutputReceiver
from brainx.binterpreter import Binterpreter
from brainx.util import *


class TestBinterpreter(unittest.TestCase):
    def test_hello_world(self):
        print("Starting hello world test")
        program = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<" \
                  ".+++.------.--------.>>+.>++.#"
        input_source = DummyInputSource(program, [])
        output_receiver = DummyOutputReceiver()
        binterpreter = Binterpreter(input_source, output_receiver)
        binterpreter.start()
        self.assertTrue(binterpreter.terminated)
        self.assertEqual("Hello World!\n", string_from_array(output_receiver.output))