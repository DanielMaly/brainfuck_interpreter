import traceback
from png_encoder import BrainlollerEncoder, BraincopterEncoder

__author__ = 'Daniel Maly'

import argparse
import sys
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
                        metavar=('source_file', 'source_image'), nargs='+')

    # The following will only work with --f2lc but there is no way to make argparse understand
    parser.add_argument("-o", "--outfile", metavar="FILE", help="Output file for --f2lc option.")
    parser.add_argument("--pnm", help="export in P6 format instead of PNG for --f2lc option", action="store_true")

    args = parser.parse_args()
    dispatch(args)
    sys.exit(0)


def dispatch(args):

    src_string = args.source
    if args.lc2f is not None:
        src_string = args.lc2f[0]
    if args.f2lc is not None:
        src_string = args.f2lc[0]

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

    elif args.f2lc is not None:
        if args.outfile is None:
            print("No output file specified. Cowarldy refusing to dump image data to a terminal.")
            sys.exit(1)

        fmt = 'png'
        if args.pnm is not None:
            fmt = 'ppm'

        if len(args.f2lc) == 1:
            BrainlollerEncoder(source.program, args.outfile, format=fmt).encode()

        else:
            BraincopterEncoder(source.program, args.f2lc[1], args.outfile, format=fmt).encode()

    else:
        output = OutputReceiver()
        start_interpreter(source, output, args.memory, args.pointer, args.steps, args.test)



def start_interpreter(source, output, memory, pointer, steps, test=False):
    binterpreter = Binterpreter(input_source=source, output_receiver=output, test=test)
    if memory is not None and len(memory) > 0:
        binterpreter.initialize_memory(memory_bytes_from_string(memory))
    binterpreter.initialize_pointer(pointer)

    if steps:
        binterpreter.print_steps = True

    binterpreter.start()


def memory_bytes_from_string(st):
    #Unwrap b'...'
    if '\'' in st:
        st = st.replace('\'', '')
        st = st.replace('x', '\\x')
    s = bytes(st[1:], "ascii").decode("unicode_escape")
    return [ord(x) for x in s]


def retrieve_source(source, debug=False):
    if source is not None:
        if set(source).issubset(set("[]-+<>#.,\"")):
            if "\"" in source:
                source = source.replace("\"", "")
            return InputSource.for_input_string(source, debug=debug)
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