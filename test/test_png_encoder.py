from binterpreter import Binterpreter
from output_receiver import OutputReceiver
from png_decoder import PNGDecoder
from test.dummy_output_receiver import DummyOutputReceiver

__author__ = 'Daniel Maly'


import unittest
from util import *
from png_encoder import BrainlollerEncoder, BraincopterEncoder, PNGWriter
from input_source import InputSource


class TestPNGEncoder(unittest.TestCase):
    def test_encode_image(self):
        filename = "tests/hello1.b"
        outname = "tmp/out.png"
        input_source = InputSource.for_file(filename)
        BrainlollerEncoder(input_source.program, outname).encode()

        source = InputSource.for_image_file("tmp/out.png")
        receiver = DummyOutputReceiver()
        Binterpreter(input_source=source, output_receiver=receiver).start()
        self.assertEqual("Hello World!\n", string_from_array(receiver.output))

        inname = "tests/Truecolor.png"
        BraincopterEncoder(input_source.program, inname, "tmp/out2.png").encode()
        source = InputSource.for_image_file("tmp/out2.png")
        receiver = DummyOutputReceiver()
        Binterpreter(input_source=source, output_receiver=receiver).start()
        self.assertEqual("Hello World!\n", string_from_array(receiver.output))
