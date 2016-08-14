#!/usr/bin/env python3

import sys
import argparse

from token import FileTokeniser, REPLTokeniser, ParseError, PseudoRuntimeError
from parse import pseudo_program
from context import Context

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
        prog = pseudo_program(parse_ctx)
        prog.eval(eval_ctx)

    except ParseError as e:
        print("Parse failed: {}".format(e))
        
    except PseudoRuntimeError as e:
        print("Runtime error: {}".format(e))
        
    #except Exception as e:
    #    print("Parser error: {}".format(e))
    
def repl():
    parse_ctx = REPLTokeniser()
    eval_ctx = Context()
    while True:
        try:
            prog = pseudo_program(parse_ctx)
            prog.eval(eval_ctx)
            
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

        except ParseError as e:
            print("Parse failed: {}".format(e))
            
        except PseudoRuntimeError as e:
            print("Runtime error: {}".format(e))

if __name__ == "__main__":
    """from io import StringIO
    buf = StringIO(source)
    parse_file(buf)"""
    repl()