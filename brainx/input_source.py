__author__ = 'Daniel Maly'

import re
import sys
import png_decoder
import util


class InputSource:

    VALID_CHARACTERS = ['<', '>', '.', ',', '+', '-', '[', ']']

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
        if decoder.is_brainloller():
            return BrainlollerInputSource(decoder, debug)
        else:
            return BraincopterInputSource(decoder, debug)

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
            # print("Waiting for input now")
            r = ord(sys.stdin.read(1))
            return r

        ret = self.input[self.input_pointer]
        self.input_pointer += 1
        return ord(ret)

    def get_debug_data(self):
        return "# program data\n" + self.program + "\n\n", ""

    def write_to_file(self, filename):
        with open(filename, 'w') as file:
            for i in range(0, len(self.program), 72):
                file.write(self.program[i:i+72])
                file.write('\n')

    def write_to_stdout(self):
        print(self.program)


#Base class for PNG sources
class PNGInputSource(InputSource):

    pointer_ops = {
            0: (lambda x, y: (x+1, y)),  # Right
            1: (lambda x, y: (x, y+1)),  # Down
            2: (lambda x, y: (x-1, y)),  # Left
            3: (lambda x, y: (x, y-1))   # Up
        }

    CMD_ROTATE_LEFT = 'L'
    CMD_ROTATE_RIGHT = 'R'

    def __init__(self, pixels, width, height, debug=False):
        self.pixels = pixels
        program = ""
        pointer_dir = 0
        pointer = (0, 0)

        instructions = []
        while pointer[0] in range(width) and pointer[1] in range(height):
            op = None
            pix = pixels[pointer[1]][pointer[0]]
            cmd = self.get_command(pix)
            if cmd in self.VALID_CHARACTERS:
                instructions.append(cmd)
            elif cmd == self.CMD_ROTATE_LEFT:
                pointer_dir -= 1
            elif cmd == self.CMD_ROTATE_RIGHT:
                pointer_dir += 1
            pointer_dir %= 4
            pointer = (self.pointer_ops[pointer_dir])(pointer[0], pointer[1])

        program = ''.join([x for x in instructions])
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

    def get_command(self, pixel):
        return ''


class BrainlollerInputSource(PNGInputSource):
    color_map = util.brainloller_color_map

    def __init__(self, decoder, debug=False):
        super().__init__(decoder.pixels,
                         debug=debug,
                         width=decoder.width,
                         height=decoder.height)

    def get_command(self, pixel):
        if pixel in self.color_map:
            return self.color_map[pixel]
        return None


class BraincopterInputSource(PNGInputSource):
    command_map = util.braincopter_command_map

    def __init__(self, decoder, debug=False):
        super().__init__(decoder.pixels,
                         debug=debug,
                         width=decoder.width,
                         height=decoder.height)

    @classmethod
    def get_command(cls, pixel):
        val = (-2 * pixel[0] + 3 * pixel[1] + pixel[2]) % 11
        if val in cls.command_map:
            cmd = cls.command_map[val]
            return cmd
        return None
