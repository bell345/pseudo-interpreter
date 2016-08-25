#!/usr/bin/env python3

import traceback
from inspect import signature

from .token import Token, PseudoRuntimeError, PseudoTypeError, PseudoBreak, PseudoContinue, PseudoReturn
from .expr import Expression, VariableReference
from .context import Context

class Statement:
    def __init__(self):
        self.context = None

    def assoc(self, ctx):
        self.context, self.row_col = ctx.get_context()
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

        return value

class IfStatement(Statement):
    def __init__(self, cond, then_stmts=[], else_stmts=[]):
        super().__init__()

        self.condition = Expression._normalise_arg(cond)
        self.then_stmt_list = then_stmts
        self.else_stmt_list = else_stmts

    def eval(self, ctx):
        res = Token('symbol', None)
        value = self.condition.eval(ctx)
        if not value:
            raise PseudoTypeError("If statement condition does not return")

        if value.type != 'number':
            raise PseudoTypeError("Condition must be numerical or boolean")

        if value.value:
            for expr in self.then_stmt_list:
                res = expr.eval(ctx)

        else:
            for expr in self.else_stmt_list:
                res = expr.eval(ctx)

        return res

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
        res = Token('symbol', None)
        self.start_expr.eval(ctx)
        while True:
            for stmt in self.stmt_list:
                try:
                    res = stmt.eval(ctx)

                except PseudoBreak:
                    return res

                except PseudoContinue:
                    break

            end = self.end_expr.eval(ctx).value
            val = self.variable.eval(ctx).value
            if val < end:
                self.variable.set(ctx, Token('number', val + 1))
            else:
                break

        return res

class WhileStatement(Statement):
    def __init__(self, cond, stmt_list=[]):
        super().__init__()

        self.condition = Expression._normalise_arg(cond)
        self.stmt_list = stmt_list

    def eval(self, ctx):
        res = Token('symbol', None)
        while self.condition.eval(ctx).value:
            for stmt in self.stmt_list:
                try:
                    res = stmt.eval(ctx)

                except PseudoBreak:
                    return res

                except PseudoContinue:
                    break

        return res

class BreakStatement(Statement):
    def eval(self, ctx):
        raise PseudoBreak(self.context)

class ContinueStatement(Statement):
    def eval(self, ctx):
        raise PseudoContinue(self.context)

class ReturnStatement(Statement):
    def __init__(self, ret):
        super().__init__()
        self.value = Expression._normalise_arg(ret)

    def eval(self, ctx):
        raise PseudoReturn(self.context, Expression._get_arg(ctx, self.value))

class PseudoProgram(Statement):
    def __init__(self, prog_name, stmt_list):
        super().__init__()
        self.name = prog_name
        self.stmt_list = stmt_list

    def eval(self, ctx, pos=None):

        name = "PROGRAM {}".format(self.name)
        if pos:
            row, col = pos
            name += ", called at line {}".format(row)

        ctx = ctx.child_context(name)

        res = Token('symbol', None)
        try:
            for stmt in self.stmt_list:
                res = stmt.eval(ctx)

        except PseudoBreak as e:
            raise PseudoRuntimeError(e.context, 'Break outside of loop') from e

        except PseudoContinue as e:
            raise PseudoRuntimeError(e.context, 'Continue outside of loop') from e

        except PseudoReturn as e:
            raise PseudoRuntimeError(e.context, 'Return outside of module') from e

        return res

class PseudoModule(Statement):
    def __init__(self, name, params, stmt_list):
        super().__init__()
        self.name = name
        self.params = params
        self.stmt_list = stmt_list

    def eval(self, ctx):
        raise PseudoRuntimeError(self.context, "Modules cannot be called like programs")

    def call(self, ctx, args, pos=None):
        args = [Expression._get_arg(ctx, Expression._normalise_arg(arg)) for arg in args]

        name = "MODULE {}".format(self.name)
        if pos:
            row, col = pos
            name += ", called at line {}".format(row)

        ctx = ctx.child_context(name)
        if len(args) != len(self.params):
            raise PseudoRuntimeError(self.context, "Module takes {} argument(s) ({} given)".format(
                    len(self.params), len(args)))

        for name, value in zip(self.params, args):
            ctx.set_var(name, value, self.context, self.row_col)

        res = Token('symbol', None)
        try:
            for stmt in self.stmt_list:
                res = stmt.eval(ctx)

        except PseudoBreak as e:
            raise PseudoRuntimeError(e.context, 'Break outside of loop')

        except PseudoContinue as e:
            raise PseudoRuntimeError(e.context, 'Continue outside of loop')

        except PseudoReturn as ret:
            return ret.value

        return res

class PseudoBinding(Statement):
    def __init__(self, name, func):
        super().__init__()

        self.name = name
        self.func = func

        self.params = [p.name for p in signature(func).parameters.values()]

    def eval(self, ctx):
        raise PseudoRuntimeError(self.context, "Modules cannot be called like programs")

    def call(self, ctx, args):
        args = [Expression._get_arg(ctx, Expression._normalise_arg(arg)).value for arg in args]

        if len(args) != len(self.params):
            raise PseudoRuntimeError(self.context, "Module takes {} argument(s) ({} given)".format(
                    len(self.params), len(args)))

        res = Token('symbol', None)
        try:
            res = self.func(*args)
            if isinstance(res, int) or isinstance(res, float):
                res = Token('number', res)
            elif res is None:
                res = Token('symbol', None)
            else:
                res = Token('string', str(res))

            return res

        except Exception as e:
            traceback.print_exc()
            raise PseudoRuntimeError(self.context, "Exception in bound module '{}'".format(self.name)) from e