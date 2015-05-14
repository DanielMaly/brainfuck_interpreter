from binterpreter import Binterpreter
from output_receiver import OutputReceiver
from png_decoder import PNGDecoder

__author__ = 'Daniel Maly'


import unittest
from util import *
from png_encoder import BrainlollerEncoder, BraincopterEncoder, PNGWriter
from input_source import InputSource


class TestPNGEncoder(unittest.TestCase):
    def test_encode_image(self):
        filename = "tests/hello1.b"
        outname = "out.png"
        input_source = InputSource.for_file(filename)
        BrainlollerEncoder(input_source.program, outname).encode()

        source = InputSource.for_image_file("out.png")
        Binterpreter(input_source=source, output_receiver=OutputReceiver()).start()

        inname = "Truecolor.png"
        decoder = PNGDecoder(inname)
        decoder.decode()
        PNGWriter("out2.png", decoder.pixels).encode()

        inname = "out2.png"
        BraincopterEncoder(input_source.program, inname, "out3.png").encode()
