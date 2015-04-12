__author__ = 'Daniel Maly'


class TextInputSource:

    @classmethod
    def for_file(cls, filename, debug=False):
        inp = None
        with open(filename, 'r') as file:
            inp = file.read()
        return cls.for_input_string(inp, debug)

    @classmethod
    def for_input_string(cls, string, debug=False):
        shplit = string.split("!")
        program = shplit[0]
        inp = ""

        if len(shplit) > 1:
            inp = shplit[1]
        if debug:
            program += "#"

        return cls(program, inp)

    def __init__(self, program, inp):
        self.program = program
        self.input = inp
        self.program_pointer = 0
        self.input_pointer = 0

    def get_next_instruction(self):
        if self.program_pointer >= len(self.program):
            return None
        ret = self.program[self.program_pointer]
        self.program_pointer += 1
        return ret

    def get_next_input(self):
        if self.input_pointer >= len(self.input):
            return None
        ret = self.input[self.input_pointer]
        self.input_pointer += 1
        return ret

    def get_debug_data(self):
        return "# program data\n" + self.program.replace("#", "") + "\n\n"