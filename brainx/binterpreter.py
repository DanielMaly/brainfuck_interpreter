__author__ = 'Daniel Maly'


class Binterpreter:
    def __init__(self, input_source, output_receiver):
        self.memory = bytearray.fromhex('00')
        self.pointer = 0
        self.terminated = False
        self.inp = input_source
        self.output = output_receiver
        self.instruction_log = []
        self.instruction_log_pointer = 0
        self.step_count = 0
        self.print_steps = False

        # print("Binterpreter constructed with program {}".format(input_source.program))

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
        if self.instruction_log_pointer >= len(self.instruction_log):
            self.instruction_log.append(self.inp.get_next_instruction())
        ret = self.instruction_log[self.instruction_log_pointer]
        self.instruction_log_pointer += 1
        return ret

    def move_previous_instruction(self):
        ret = self.instruction_log[self.instruction_log_pointer - 1]
        self.instruction_log_pointer -= 1
        return ret

    def step(self):
        instruction = self.move_next_instruction()
        if instruction is None:
            self.terminate()

        self.step_count += 1

        if self.print_steps and self.step_count % 10000 == 0:
            print("S " + str(self.step_count) + " ## I " + str(self.instruction_log_pointer) + " ## MP " + str(self.pointer) + " ## MV " +
              str(self.memory[self.pointer]) + " ## X " + str(instruction))

        options = {
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

        if instruction in options:
            func = options[instruction]
            func()

    def move_left(self):
        if self.pointer != 0:
            self.pointer -= 1

    def move_right(self):
        self.pointer += 1
        if self.pointer >= len(self.memory):
            self.memory.append(0x00)

    def increment(self):
        if self.memory[self.pointer] == 0xFF:
            self.memory[self.pointer] = 0x00
        else:
            self.memory[self.pointer] += 1

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

    def close_loop(self):
        if self.memory[self.pointer] != 0x00:
            opened_loops_count = 1
            self.move_previous_instruction()
            while opened_loops_count > 0:
                instr = self.move_previous_instruction()
                if instr == '[':
                    opened_loops_count -= 1
                elif instr == ']':
                    opened_loops_count += 1
            self.move_next_instruction()
