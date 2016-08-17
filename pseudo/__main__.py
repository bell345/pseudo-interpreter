#!/usr/bin/env python3

import sys
import argparse

from .version import APP_NAME, APP_VERSION
from .token import FileTokeniser, REPLTokeniser, ParseError, PseudoRuntimeError
from .parse import pseudo_code_element
from .context import Context

source = """
PROGRAM rectangle_area_and_perimeter
BEGIN
    max <- -INF
    FOR n <- 1 TO 3
        INPUT (new_num)
        IF (new_num > max) THEN
            max <- new_num
        END IF
    NEXT
    OUTPUT (max)
END
"""

def parse_file(fp):
    parse_ctx = FileTokeniser(fp)
    eval_ctx = Context()
    try:
        prog = pseudo_code_element(parse_ctx)
        prog.eval(eval_ctx)

    except ParseError as e:
        print("Parse failed: {}".format(e))

    except PseudoRuntimeError as e:
        print("Runtime error: {}".format(e))

    #except Exception as e:
    #    print("Parser error: {}".format(e))

def repl():
    print("{} version {}".format(APP_NAME, APP_VERSION))
    print("(C) Thomas Bell 2016, MIT License.")
    print("Press Ctrl-C to exit.")

    parse_ctx = REPLTokeniser()
    eval_ctx = Context()
    while True:
        try:
            prog = pseudo_code_element(parse_ctx)
            prog.eval(eval_ctx)

        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

        except ParseError as e:
            print("Parse failed: {}".format(e))
            parse_ctx.reset()

        except PseudoRuntimeError as e:
            print("Runtime error: {}".format(e))

def main():

    parser = argparse.ArgumentParser(prog=APP_NAME,
            description="An interpreter for simple PASCAL-like pseudo code.",
            epilog="(C) Thomas Bell 2016, MIT License.")
    parser.add_argument("--version", action="version", version=APP_VERSION)

    parser.add_argument("input_file", type=argparse.FileType('r'), nargs="?",
            help="Input source file to be interpreted.")

    args = parser.parse_args()

    if args.input_file:
        parse_file(args.input_file)

    else:
        repl()

if __name__ == "__main__":
    """from io import StringIO
    buf = StringIO(source)
    parse_file(buf)"""
    #repl()
    main()