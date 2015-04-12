__author__ = 'Daniel Maly'

import sys
import glob

class OutputReceiver:
    def __init__(self):
        self.output = []
        self.debug_info = None
        self.print_to_stdout = True
        self.print_debug_to_stdout = False

    def put_char(self, char):
        self.output.append(char)
        if self.print_to_stdout:
            sys.stdout.write(char)

    def output_bytes(self):
        return bytes(self.output)

    def get_debug_data(self, input_debug_data, binterpreter):
        memory = "# memory\n" + str(bytes(binterpreter.memory)) + "\n\n"
        memory_pointer = "# memory pointer\n" + str(binterpreter.pointer) + "\n\n"
        output = "# output\n" + str(self.output_bytes()) + "\n\n"

        debug_info = input_debug_data + memory + memory_pointer + output
        return debug_info

    def get_suitable_file_number(self):
        numbers = set([int(f[6:8]) for f in glob.glob("debug_[0-9][0-9].log")])
        available = set(range(100)) - numbers
        return sorted(list(available))[0]


    def print_debug_data(self, input_debug_data, binterpreter):
        number = str(self.get_suitable_file_number()).zfill(2)
        filename = "debug_" + number + ".log"
        debug_data = self.get_debug_data(input_debug_data, binterpreter)

        if self.print_debug_to_stdout:
            print(debug_data)

        with open(filename, 'w') as file:
            file.write(debug_data)
