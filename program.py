#!/usr/bin/env python3

from token import PseudoBreak, PseudoContinue, PseudoRuntimeError

class PseudoProgram:
    def __init__(self, prog_name, stmt_list):
        self.name = prog_name
        self.stmt_list = stmt_list
        
    def eval(self, ctx):
        try:
            for stmt in self.stmt_list:
                stmt.eval(ctx)
                
        except PseudoBreak:
            raise PseudoRuntimeError('Break outside of loop')
            
        except PseudoContinue:
            raise PseudoRuntimeError('Continue outside of loop')
