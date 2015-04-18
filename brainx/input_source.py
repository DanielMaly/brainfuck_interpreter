__author__ = 'Daniel Maly'

import re
import sys
import png_decoder


class InputSource:

    @classmethod
    def for_file(cls, filename, debug=False):
        inp = None
        with open(filename, 'r') as file:
            inp = file.read()
        return cls.for_input_string(inp, debug)

    @classmethod
    def for_image_file(cls, filename, debug=False):
        decoder = png_decoder.PNGDecoder(filename)
        decoder.decode()
        return BrainlollerInputSource(decoder, debug)

    @classmethod
    def for_input_string(cls, string, debug=False):
        rgxp = "[^<>+\-#.,\[\]]"
        shplit = string.split("!")
        program = re.sub(rgxp, "", shplit[0])
        inp = ""
        if len(shplit) > 1:
            inp = shplit[1]
        return cls(program, inp, debug)

    @classmethod
    def for_interactive_string(cls, debug=False):
        return cls.for_input_string(sys.stdin.readline())

    def __init__(self, program, inp, debug=False):
        self.program = program
        self.input = inp
        self.program_pointer = 0
        self.input_pointer = 0
        self.debug = debug

    def get_next_instruction(self):
        if self.program_pointer >= len(self.program):
            if self.program_pointer == len(self.program) and self.debug:
                self.program_pointer += 1
                return "#"
            return None
        ret = self.program[self.program_pointer]
        self.program_pointer += 1
        return ret

    def get_next_input(self):
        if self.input_pointer >= len(self.input):
            return ord(sys.stdin.read(1))
        ret = self.input[self.input_pointer]
        self.input_pointer += 1
        return ord(ret)

    def get_debug_data(self):
        return "# program data\n" + self.program + "\n\n", ""

    def write_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(self.program)
            file.write('\n')

    def write_to_stdout(self):
        print(self.program)


#Base class for PNG sources
class PNGInputSource(InputSource):
    color_map = {
        b'\xff\x00\x00': '>',
        b'\x80\x00\x00': '<',
        b'\x00\xff\x00': '+',
        b'\x00\x80\x00': '-',
        b'\x00\x00\xff': '.',
        b'\x00\x00\x80': ',',
        b'\xff\xff\x00': '[',
        b'\x80\x80\x00': ']',
        }

    ROTATE_LEFT = b'\x00\x80\x80'
    ROTATE_RIGHT = b'\x00\xff\xff'

    pointer_ops = {
            0: (lambda x, y: (x+1, y)),  # Right
            1: (lambda x, y: (x, y+1)),  # Down
            2: (lambda x, y: (x-1, y)),  # Left
            3: (lambda x, y: (x, y-1))   # Up
        }

    def __init__(self, pixels, width, height, debug=False):
        self.pixels = pixels
        program = ""
        pointer_dir = 0
        pointer = (0, 0)
        while pointer[0] in range(width) and pointer[1] in range(height):
            op = None
            pix = pixels[pointer[1]][pointer[0]]
            if pix in self.color_map:
                program += self.color_map[pix]
                # print("Read pix {} translated to {}".format(pix, color_map[pix]))
            elif pix == self.ROTATE_LEFT:
                pointer_dir -= 1
            elif pix == self.ROTATE_RIGHT:
                pointer_dir += 1
            pointer_dir %= 4
            pointer = (self.pointer_ops[pointer_dir])(pointer[0], pointer[1])

        super().__init__(program, [], debug)

    def get_debug_data(self):
        dd = super().get_debug_data()
        rgbinput = "# RGB input\n[\n"

        for row in self.pixels:
            rgbinput += "    ["
            for pix in row:
                rgbinput += "({}, {}, {}), ".format(int(pix[0]), int(pix[1]), int(pix[2]))
            rgbinput = rgbinput[:-2]
            rgbinput += "],\n"

        rgbinput += "]\n\n"
        return dd[0], rgbinput


class BrainlollerInputSource(PNGInputSource):
    def __init__(self, decoder, debug=False):
        super().__init__(decoder.pixels,
                         debug=debug,
                         width=decoder.width,
                         height=decoder.height)


class BraincopterInputSource(PNGInputSource):
    def __init__(self, decoder, debug=False):
        convert_func = lambda r, g, b: (-2 * r, 3 * g, )
        pixels = []
        for row in decoder.pixels:
            nrow = []
            for pix in row:
                nrow.append([])
        super().__init__(pixels,
                         debug=debug,
                         width=decoder.width,
                         height=decoder.height)