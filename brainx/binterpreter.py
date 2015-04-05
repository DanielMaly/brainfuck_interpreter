__author__ = 'Daniel Maly'


class Binterpreter:
    def __init__(self, input_source, output_source):
        self.memory = bytearray.fromhex('00')
        self.pointer = 0
        self.terminated = False
        self.inp = input_source
        self.output = output_source
        self.instruction_log = []
        self.instruction_log_pointer = 0

    def initialize_memory(self, memory):
        self.memory = memory

    def initialize_pointer(self, position):
        self.pointer = position

    def terminate(self):
        self.terminated = True

    def print_debug_info(self):
        pass

    def move_next_instruction(self):
        if self.instruction_log_pointer >= len(self.instruction_log):
            self.instruction_log.append(self.inp.get_next_instruction())
        ret = self.instruction_log[self.instruction_log_pointer]
        self.instruction_log_pointer += 1
        return ret

    def move_previous_instruction(self):
        ret = self.instruction_log_pointer[self.instruction_log_pointer - 1]
        self.instruction_log_pointer += 1
        return ret

    def step(self):
        instruction = self.move_next_instruction()
        if instruction is None:
            self.terminate()

        options = {
            '#' : self.print_debug_info,
            '<' : self.move_left,
            '>' : self.move_right,
            '.' : self.out,
            ',' : self.read,
            '+' : self.increment,
            '-' : self.decrement,
            '[' : self.open_loop,
            ']' : self.close_loop
        }

        if instruction in options:
            func = options[instruction]
            func()

    def move_left(self):
        if self.pointer != 0:
            self.pointer -= 1

    def move_right(self):
        self.pointer += 1

    def increment(self):
        if self.memory[self.pointer] == 0xFF:
            self.memory[self.pointer] = 0x00
        else:
            self.memory[self.pointer] += 1;

    def decrement(self):
        if self.memory[self.pointer] == 0x00:
            self.memory[self.pointer] = 0xFF
        else:
            self.memory[self.pointer] -= 1;

    def out(self):
        self.output.put_char(self.memory[self.pointer])

    def read(self):
        byte = self.inp.get_next_input()
        self.memory[self.pointer] = byte

    def open_loop(self):
        if self.memory[self.pointer] == 0x00:
            while self.move_next_instruction() != ']':
                pass

    def close_loop(self):
        if self.memory[self.pointer] != 0x00:
            while self.move_previous_instruction() != '[':
                pass
            self.move_next_instruction()








