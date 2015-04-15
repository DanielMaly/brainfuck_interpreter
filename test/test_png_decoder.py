__author__ = 'Daniel Maly'

import unittest
from util import *
from png_decoder import PNGDecoder, PNGNotImplementedError, PNGWrongHeaderError


class TestPNGDecoder(unittest.TestCase):
    def test_decode_image(self):
        decoder = PNGDecoder("tests/HelloWorld.png")
        decoder.decode()
        print(decoder.pixels)
        self.assertEqual(14 * 12, len(decoder.pixels))