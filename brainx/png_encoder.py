import zlib
import util
import struct
from png_decoder import PNGDecoder

__author__ = 'Daniel Maly'

# Common PNG writer with pixels already ready

# Grid generator for given width, height and program

# Pixel generator for brainloller given a grid

# Pixel generator for braincopter given the source image and the grid

# Brainloller encoder: Program -> optimal width and height -> grid -> pixels -> write PNG
# Braincopter encoder: Program, source image -> grid -> source image + grid -> pixels -> write PNG


class PNGWriter:
    def __init__(self, filename, pixels):
        self.filename = filename
        self.pixels = pixels

    def encode(self):
        header_bytes = PNGDecoder.PNG_HEADER
        special_bytes = PNGDecoder.SPECIAL_FIELDS
        width = len(self.pixels[0])
        width_bytes = struct.pack(">I", width)
        height_bytes = struct.pack(">I", len(self.pixels))

        with open(self.filename, 'wb') as file:
            file.write(header_bytes)
            header_chunk = self.make_chunk("IHDR", width_bytes + height_bytes + special_bytes)
            file.write(header_chunk)

            # encode scanlines
            scanlines = bytearray()
            prev_row = ['\x00' for i in range(width)]
            for row in self.pixels:
                scanline = self.encode_scanline(row, prev_row)
                prev_row = row
                scanlines.extend(scanline)

            # compress
            data = zlib.compress(scanlines)

            # write IDAT
            CHUNK_SIZE = 1024
            for i in range(len(data) // CHUNK_SIZE + 1):
                chunk_data = data[i*CHUNK_SIZE:(i+1)*CHUNK_SIZE]
                chunk = self.make_chunk("IDAT", chunk_data)
                file.write(chunk)

            # write IEND
            end_chunk = self.make_chunk("IEND", b'')
            file.write(end_chunk)

    @staticmethod
    def make_chunk(name, data):
        length_bytes = struct.pack(">I", len(data))
        chunk_name = name.encode("ascii")
        crc = struct.pack(">I", zlib.crc32(chunk_name + data))
        chunk = length_bytes + chunk_name + data + crc
        return chunk

    @staticmethod
    def encode_scanline(row, prev_row):
        # Don't use any filters
        return b'\x00' + bytes([bts for pix in row for bts in pix])


class GridMaker:
    def __init__(self, program, width, height):
        self.program = program
        self.width = width
        self.height = height

    # This will return a grid of BRAINFUCK commands. Nop is represented by 'N'.
    # Turns are represented by R,L
    # The grid is constructed from the top left in rows
    def make_grid(self):

        program = self.program
        grid = []

        for row in range(self.height):
            assembled_row = []
            for column in range(self.width):
                if row > 0 and column == 0:
                    assembled_row.append('L')
                elif row < self.height - 1 and column == self.width - 1:
                    assembled_row.append('R')
                elif len(program) > 0:
                    if row % 2 == 0:
                        assembled_row.append(program[0])
                    else:
                        assembled_row.insert(1, program[0])
                    program = program[1:]
                else:
                    assembled_row.append('N')
            grid.append(assembled_row)

        return grid


class BrainlollerEncoder:
    def __init__(self, program, filename):
        self.program = program
        self.filename = filename

    def encode(self):
        # First we get the optimal width and height
        width, height = self.optimal_width_and_height()

        # Then we make the command grid (common part with braincopter)
        grid = GridMaker(self.program, width, height).make_grid()

        # Then we convert the grid into pixels
        pixels = self.pixelize(grid)

        # Then we pass it to the PNG writer (common part with braincopter)
        PNGWriter(self.filename, pixels).encode()

    def optimal_width_and_height(self):
        length = len(self.program)
        fits = lambda w, h: (w-2) * h + 2

        width, height = 3, 3
        while fits(width, height) < length:
            if width > height:
                height += 1
            else:
                width += 1

        print("Computed optimal width and height: {},{}".format(width, height))
        return width, height

    @staticmethod
    def pixelize(grid):
        inv_colors = {v: k for k, v in util.brainloller_color_map.items()}
        inv_colors['N'] = b'\x00\x00\x00'
        return [[inv_colors[command] for command in row] for row in grid]


class BraincopterEncoder:
    def __init__(self, program, source, destination):
        self.program = program
        self.source = source
        self.destination = destination

    def encode(self):
        decoder = PNGDecoder(self.source)
        decoder.decode()
        width, height = decoder.width, decoder.height
        pixels = decoder.pixels

        grid = GridMaker(self.program, width, height).make_grid()
        encoded = self.pixelize(pixels, grid)

        PNGWriter(self.destination, encoded).encode()

    @classmethod
    def pixelize(cls, source, grid):
        rows = []
        for i in range(len(grid)):
            source_row = source[i]
            enc_row = []
            for j in range(len(source_row)):
                enc_row.append(cls.closest_color(source_row[j], grid[i][j]))
            rows.append(enc_row)

        return rows

    @staticmethod
    def closest_color(pixel, command):
        inv_numbers = {v: k for k, v in util.braincopter_command_map.items()}