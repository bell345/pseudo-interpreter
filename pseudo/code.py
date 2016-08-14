#!/usr/bin/env python3

from .token import Token, PseudoRuntimeError, PseudoTypeError, PseudoBreak, PseudoContinue
from .expr import Expression, VariableReference

class Statement:
    def __init__(self):
        self.context = None

    def assoc(self, ctx):
        self.context = ctx.get_context()
        return self

class AssignmentStatement(Statement):
    def __init__(self, target, value):
        super().__init__()

        self.target = Expression._normalise_arg(target)
        if not isinstance(self.target, VariableReference):
            raise PseudoTypeError("Assignment target must be a variable reference")

        self.value = Expression._normalise_arg(value)

    def eval(self, ctx):
        value = Expression._get_arg(ctx, self.value)

        self.target.set(ctx, value)

class IfStatement(Statement):
    def __init__(self, cond, then_stmts=[], else_stmts=[]):
        super().__init__()

        self.condition = Expression._normalise_arg(cond)
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
        if not isinstance(start_expr, AssignmentStatement):
            raise PseudoTypeError("For statement requires a variable assignment")

        self.variable = start_expr.target

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
        while self.condition.eval(ctx).value:
            for stmt in self.stmt_list:
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

class PseudoProgram(Statement):
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
