#!/usr/bin/env python3

from token import Token, PseudoTypeError, PseudoBreak, PseudoContinue
from expr import Expression, VariableReference

class Statement:
    def __init__(self):
        pass
        
class IfStatement(Statement):
    def __init__(self, cond, then_stmts=[], else_stmts=[]):
        super().__init__()
        
        self.condition = cond
        self.then_stmt_list = then_stmts
        self.else_stmt_list = else_stmts
        
    def eval(self, ctx):
        value = self.condition.eval(ctx)
        if not value:
            raise PseudoTypeError("If statement condition does not return")
            
        if value.type != 'number':
            raise PseudoTypeError("Condition must be numerical or boolean")
            
        if value.value:
            for expr in self.then_stmt_list:
                expr.eval(ctx)
                
        else:
            for expr in self.else_stmt_list:
                expr.eval(ctx)
                
class ForStatement(Statement):
    def __init__(self, start_expr, end_expr, stmt_list=[]):
        super().__init__()
        
        self.start_expr = start_expr
        self.variable = start_expr.argument1
        if not isinstance(self.variable, VariableReference):
            raise PseudoTypeError("For statement requires a variable assignment")

        self.end_expr = Expression._normalise_arg(end_expr)
        self.stmt_list = stmt_list
        
    def eval(self, ctx):
        self.start_expr.eval(ctx)
        while True:
            broken = False
            for stmt in self.stmt_list:
                try:
                    stmt.eval(ctx)
                    
                except PseudoBreak:
                    return
                    
                except PseudoContinue:
                    break
                
            end = self.end_expr.eval(ctx).value
            val = self.variable.eval(ctx).value
            if val < end:
                self.variable.set(ctx, Token('number', val + 1))
            else:
                break
                
class WhileStatement(Statement):
    def __init__(self, cond, stmt_list=[]):
        super().__init__()
        
        self.condition = Expression._normalise_arg(cond)
        self.stmt_list = stmt_list
        
    def eval(self, ctx):
        while self.condition.eval().value:
            for stmt in stmt_list:
                try:
                    stmt.eval(ctx)
                
                except PseudoBreak:
                    return
                    
                except PseudoContinue:
                    break
                
class BreakStatement(Statement):
    def __init__(self):
        super().__init__()
        
    def eval(self):
        raise PseudoBreak
        
class ContinueStatement(Statement):
    def __init__(self):
        super().__init__()
        
    def eval(self):
        raise PseudoContinue