__author__ = 'Daniel Maly'

import zlib
import struct

class PNGWrongHeaderError(BaseException):
    pass


class PNGNotImplementedError(BaseException):
    pass


class CRCError(BaseException):
    pass


class PNGDecoder:
    PNG_HEADER = bytes.fromhex("89 50 4E 47 0D 0A 1A 0A")
    IHDR = b'\x00\x00\x00\rIHDR'
    IEND = b'\x00\x00\x00\x00IEND'
    SPECIAL_FIELDS = bytes.fromhex("08 02 00 00 00")

    def __init__(self, filename):
        self.filename = filename
        self.pixels = []

    def decode(self):
        with open(self.filename, 'rb') as file:
            width, height = self.read_png_header(file)
            while self.read_chunk(file, width)[0] != self.IEND:
                self.read_chunk()

    def read_png_header(self, file):
        #Read PNG header
        b = file.read(8)
        if b is None or b != self.PNG_HEADER:
            raise PNGWrongHeaderError()

        #Read IHDR chunk
        b = file.read(25)
        if b is None or b[:8] != self.IHDR or len(b) < 25:
            raise PNGWrongHeaderError()
        if not self.crc_chunk(b[4:-4], b[-4:]):
            raise CRCError()
        width, height = struct.unpack(">II", b[8:16])
        if b[16:21] != self.SPECIAL_FIELDS:
            raise PNGNotImplementedError()

        return width, height

    def read_chunk(self, file, width):
        h = file.read(8)
        if h == self.IEND:
            return self.IEND, None

        data_length = struct.unpack(">I", h[:4])[0]
        d = file.read(data_length + 4)
        data, crc = d[:-4], d[-4:]

        if not self.crc_chunk(h[4:] + data, crc):
            raise CRCError()

        uncompressed = zlib.decompress(data)
        step = 3*width + 1
        for i in range(0, len(uncompressed), step):
            row = uncompressed[i:(i + step)]
            filter = row[0]
            if filter != 0x00:
                raise PNGNotImplementedError()
            for j in range(1, width, 3):
                pixel = row[j:(j+3)]
                red, green, blue = struct.unpack("BBB", pixel)
                self.pixels.append((red, green, blue))

    def crc_chunk(self, data, crc):
        correct_crc = zlib.crc32(data)
        crc_code = struct.unpack(">I", crc)[0]
        return crc_code == correct_crc
