#!/usr/bin/env python3

import sys
import argparse

from .version import APP_NAME, APP_VERSION
from .token import Token, FileTokeniser, REPLTokeniser, ParseError, PseudoRuntimeError
from .code import PseudoModule, PseudoProgram
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

def parse(parse_ctx):
    global_ctx = Context()
    while True:
        try:
            el = pseudo_code_element(parse_ctx)
            if isinstance(el, PseudoModule):
                global_ctx.def_module(el.name, el)

            elif isinstance(el, PseudoProgram):
                global_ctx.def_program(el.name, el)

            else:
                res = el.eval(global_ctx)
                if res is not None and res != Token('symbol', None):
                    print(res.value)

        except KeyboardInterrupt as e:
            if parse_ctx.level > 1:
                print("")
                parse_ctx.reset()
            else:
                print("KeyboardInterrupt")
                sys.exit(0)

        except EOFError as e:
            break

        except ParseError as e:
            print("Parse failed: {}".format(e))
            parse_ctx.reset()
            #sys.exit(1)

        except PseudoRuntimeError as e:
            print("Runtime error: {}".format(e))
            #sys.exit(1)

    return global_ctx

def parse_file(fp):
    ctx = parse(FileTokeniser(fp))
    if len(ctx.programs) == 0:
        return

    elif len(ctx.programs) == 1:
        try:
            for prog in ctx.programs.values():
                prog.eval(ctx)

        except EOFError as e:
            pass

        except ParseError as e:
            print("Parse failed: {}".format(e))
            parse_ctx.reset()
            #sys.exit(1)

        except PseudoRuntimeError as e:
            print("Runtime error: {}".format(e))
            #sys.exit(1)

    elif 'main' not in ctx.programs:
        print("Your code file does not have a main entry point.")
        while True:
            print("Select a program from the list below (or enter nothing to exit):")
            keys = ctx.programs.keys()
            for name in enumerate(keys):
                print(name)

            name = input(": ")
            if not name:
                break

            elif name not in keys:
                print("The program you entered has not been defined.")
                continue

            else:
                prog = ctx.get_program(name)
                if prog: prog.eval(ctx)

def repl():
    print("{} version {}".format(APP_NAME, APP_VERSION))
    print("(C) Thomas Bell 2016, MIT License.")
    print("Press Ctrl-C to exit.")

    ctx = parse(REPLTokeniser())

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