__author__ = 'Daniel Maly'

import zlib
import struct
import util


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

    LAST_CHUNK = 0
    MORE_CHUNKS = 1

    def __init__(self, filename):
        self.filename = filename
        self.pixels = []
        self.chunks = bytearray()
        self.width = 0
        self.height = 0

    def decode(self):
        with open(self.filename, 'rb') as file:
            width, height = self.read_png_header(file)
            self.width = width
            self.height = height
            while self.read_chunk(file, width) != self.LAST_CHUNK:
                pass
            self.process_chunks()

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
            return self.LAST_CHUNK

        data_length = struct.unpack(">I", h[:4])[0]
        d = file.read(data_length + 4)
        data, crc = d[:-4], d[-4:]

        if not self.crc_chunk(h[4:] + data, crc):
            raise CRCError()

        self.chunks.extend(data)

        return self.MORE_CHUNKS

    def process_chunks(self):
        uncompressed = zlib.decompress(self.chunks)
        self.pixels = self.unfilter(uncompressed, self.width)

    def unfilter(self, data, width):
        filter_funcs = {
            0: (lambda x, a, b, c: x),
            1: (lambda x, a, b, c: x + a),
            2: (lambda x, a, b, c: x + b),
            3: (lambda x, a, b, c: (a + b) // 2),
            4: (lambda x, a, b, c: x + util.paeth(a, b, c))
        }

        unfilt = []
        step = 3*width + 1
        prev_row_index = -1
        for i in range(0, len(data), step):
            print("i is {} / {}".format(i, len(data)))
            previous_row = None
            if prev_row_index >= 0:
                previous_row = unfilt[prev_row_index]

            row = data[i:(i+step)]
            filter = row[0]

            apix = bytes.fromhex("00 00 00")
            bpix = bytes.fromhex("00 00 00")
            cpix = bytes.fromhex("00 00 00")

            recon_row = []
            for j in range(1, len(row), 3):
                pix = row[j:(j+3)]
                if previous_row is not None:
                    bpix = previous_row[j // 3]

                if len(recon_row) > 0:
                    apix = recon_row[(j // 3) - 1]
                    if previous_row is not None:
                        cpix = previous_row[(j // 3) - 1]

                xpix = struct.unpack("BBB", pix)
                npix = bytearray()

                for k in range(3):
                    unfilt_pix = (filter_funcs[filter])(xpix[k], apix[k], bpix[k], cpix[k]) % 256
                    npix.append(unfilt_pix)
                recon_row.append(bytes(npix))

            prev_row_index += 1
            unfilt.append(recon_row)

        return unfilt

    def crc_chunk(self, data, crc):
        correct_crc = zlib.crc32(data)
        crc_code = struct.unpack(">I", crc)[0]
        return crc_code == correct_crc

    def is_brainloller(self):
        flattened = [pix for row in self.pixels for pix in row]
        for pix in flattened:
            if pix not in util.brainloller_color_map:
                return False
        return True
