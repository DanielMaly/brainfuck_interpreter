__author__ = 'Daniel Maly'

import argparse
import sys
import struct
from binterpreter import Binterpreter
from input_source import TextInputSource
from output_receiver import OutputReceiver

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("source", help="input file or brainfuck code enclosed in quotes", nargs="?")
    parser.add_argument("-t", "--test", help="print debug output at the end of execution", action="store_true")
    parser.add_argument("-s", "--steps", help="print brainfuck interpreter output at each step", action="store_true")
    parser.add_argument("-m", "--memory", help="initial memory state", metavar="b'...'")
    parser.add_argument("-p", "--pointer", help="initial pointer location", metavar='N', type=int, default=0)

    args = parser.parse_args()
    dispatch(args)
    sys.exit(0)


def dispatch(args):
    source = retrieve_source(args.source, debug=args.test)
    output = OutputReceiver()
    start_interpreter(source, output, args.memory, args.pointer, args.steps)


def start_interpreter(source, output, memory, pointer, steps):
    binterpreter = Binterpreter(input_source=source, output_receiver=output)
    if memory is not None and len(memory) > 0:
        binterpreter.initialize_memory(memory_bytes_from_string(memory))
    binterpreter.initialize_pointer(pointer)

    if steps:
        binterpreter.print_steps = True

    binterpreter.start()


def memory_bytes_from_string(st):
    #Unwrap b'...'
    s = bytes(st[2:-1], "ascii").decode("unicode_escape")
    return [ord(x) for x in s]

def retrieve_source(source, debug=False):
    if source is not None:
        if source[0] == '"' and source[-1] == '"':
            return TextInputSource.for_input_string(source[1:-1], debug=debug)
        else:
            return TextInputSource.for_file(source, debug=debug)
    else:
        #Interpreter mode
        return TextInputSource.for_interactive_string(debug=debug)

if __name__ == "__main__":
    main()