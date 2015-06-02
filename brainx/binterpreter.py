__author__ = 'Daniel Maly'


class Binterpreter:
    def __init__(self, input_source, output_receiver, test=False):
        self.memory = bytearray.fromhex('00')
        self.pointer = 0
        self.terminated = False
        self.inp = input_source
        self.output = output_receiver
        self.program = input_source.program
        self.program_pointer = 0
        self.step_count = 0
        self.print_steps = False
        self.loop_stack = []
        self.test = test

        self.options = {
            '#': self.print_debug_info,
            '<': self.move_left,
            '>': self.move_right,
            '.': self.out,
            ',': self.read,
            '+': self.increment,
            '-': self.decrement,
            '[': self.open_loop,
            ']': self.close_loop
        }

    def initialize_memory(self, memory):
        self.memory = bytearray(memory)

    def initialize_pointer(self, position):
        self.pointer = position

    def start(self):
        while not self.terminated:
            self.step()

    def terminate(self):
        self.terminated = True

    def print_debug_info(self):
        input_debug_data = self.inp.get_debug_data()
        self.output.print_debug_data(input_debug_data, self)

    def move_next_instruction(self):
        if self.program_pointer >= len(self.program):
            if self.test:
                self.print_debug_info()
            self.terminate()
            return 'N'
        self.program_pointer += 1
        return self.program[self.program_pointer-1]

    def move_previous_instruction(self):
        self.program_pointer -= 1
        ret = self.program[self.program_pointer]
        return ret

    def step(self):
        instruction = self.move_next_instruction()

        self.step_count += 1

        if self.print_steps:
            print("S " + str(self.step_count) + " ## I " + str(self.program_pointer) + " ## MP " + str(self.pointer) + " ## MV " +
              str(self.memory[self.pointer]) + " ## X " + str(instruction))


        if instruction in self.options:
            self.options[instruction]()

    def move_left(self):
        if self.pointer != 0:
            self.pointer -= 1

    def move_right(self):
        self.pointer += 1
        if self.pointer >= len(self.memory):
            self.memory.append(0x00)

    def increment(self):
        temp = self.memory[self.pointer] + 1
        self.memory[self.pointer] = temp % 256

    def decrement(self):
        if self.memory[self.pointer] == 0x00:
            self.memory[self.pointer] = 0xFF
        else:
            self.memory[self.pointer] -= 1

    def out(self):
        self.output.put_char(self.memory[self.pointer])

    def read(self):
        byte = self.inp.get_next_input()
        self.memory[self.pointer] = byte

    def open_loop(self):
        if self.memory[self.pointer] == 0x00:
            closed_loops_count = 1
            while closed_loops_count > 0:
                instr = self.move_next_instruction()
                if instr == ']':
                    closed_loops_count -= 1
                elif instr == '[':
                    closed_loops_count += 1

        else:
            self.loop_stack.append(self.program_pointer)

    def close_loop(self):
        if self.memory[self.pointer] != 0x00:

            if len(self.loop_stack) > 0:
                open_loop_index = self.loop_stack[-1]
                self.program_pointer = open_loop_index
                return

            opened_loops_count = 1
            self.move_previous_instruction()
            while opened_loops_count > 0:
                instr = self.move_previous_instruction()
                if instr == '[':
                    opened_loops_count -= 1
                elif instr == ']':
                    opened_loops_count += 1
            self.move_next_instruction()

        else:
            self.loop_stack.pop()
