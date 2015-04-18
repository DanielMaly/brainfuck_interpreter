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


class BrainlollerInputSource(InputSource):
    def __init__(self, decoder, debug=False):
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

        program = ""
        pointer_dir = 0
        pointer = (0, 0)
        while pointer[0] in range(decoder.width) and pointer[1] in range(decoder.height):
            op = None
            pix = decoder.pixels[pointer[1]][pointer[0]]
            if pix in color_map:
                program += color_map[pix]
                # print("Read pix {} translated to {}".format(pix, color_map[pix]))
            elif pix == ROTATE_LEFT:
                pointer_dir -= 1
            elif pix == ROTATE_RIGHT:
                pointer_dir += 1
            pointer_dir %= 4
            pointer = (pointer_ops[pointer_dir])(pointer[0], pointer[1])

        self.decoder = decoder
        super().__init__(program, [], debug)

    def get_debug_data(self):
        dd = super().get_debug_data()
        rgbinput = "# RGB input\n[\n"

        for row in self.decoder.pixels:
            rgbinput += "    ["
            for pix in row:
                rgbinput += "({}, {}, {}), ".format(int(pix[0]), int(pix[1]), int(pix[2]))
            rgbinput = rgbinput[:-2]
            rgbinput += "],\n"

        rgbinput += "]\n\n"
        return dd[0], rgbinput