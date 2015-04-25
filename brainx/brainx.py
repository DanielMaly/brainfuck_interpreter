import traceback

__author__ = 'Daniel Maly'

import argparse
import sys
import struct
import re
from binterpreter import Binterpreter
from input_source import InputSource
from output_receiver import OutputReceiver
from png_decoder import PNGNotImplementedError, PNGWrongHeaderError


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("source", help="input file or brainfuck code enclosed in quotes", nargs="?")
    parser.add_argument("-t", "--test", help="print debug output at the end of execution", action="store_true")
    parser.add_argument("-s", "--steps", help="print brainfuck interpreter output at each step", action="store_true")
    parser.add_argument("-m", "--memory", help="initial memory state", metavar="b'...'")
    parser.add_argument("-p", "--pointer", help="initial pointer location", metavar='N', type=int, default=0)
    parser.add_argument("--lc2f", help="translate input image to regular brainfuck source",
                        metavar=('source_image', 'destination_file'), nargs='+')
    parser.add_argument("--f2lc", help="translate input program to a brainloller / braincopter image",
                        metavar=('source_file', ''), nargs='+')

    args = parser.parse_args()
    dispatch(args)
    sys.exit(0)


def dispatch(args):
    src_string = args.source
    if args.lc2f is not None:
        src_string = args.lc2f[0]
    
    try:
        source = retrieve_source(src_string, debug=args.test)
    except PNGWrongHeaderError as ex:
        traceback.print_exc()
        sys.exit(4)
    except PNGNotImplementedError as ex:
        traceback.print_exc()
        sys.exit(8)
    
    if args.lc2f is not None:
        if len(args.lc2f) < 2:
            source.write_to_stdout()
        else:
            source.write_to_file(args.lc2f[1])
    else:
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
            return InputSource.for_input_string(source[1:-1], debug=debug)
        else:
            try:
                return InputSource.for_file(source, debug=debug)
            except UnicodeDecodeError as ex:
                return InputSource.for_image_file(source, debug=debug)
    else:
        #Interpreter mode
        return InputSource.for_interactive_string(debug=debug)

if __name__ == "__main__":
    main()