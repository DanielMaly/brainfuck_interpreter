__author__ = 'Daniel Maly'

import re
import sys

class TextInputSource:

    @classmethod
    def for_file(cls, filename, debug=False):
        inp = None
        with open(filename, 'r') as file:
            inp = file.read()
        return cls.for_input_string(inp, debug)

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
        return "# program data\n" + self.program + "\n\n"