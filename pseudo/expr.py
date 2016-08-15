#!/usr/bin/env python3

from .token import *

class Expression:
    def __init__(self):
        self.context = None

    def assoc(self, ctx):
        self.context = ctx.get_context()
        return self

    @staticmethod
    def _get_arg(ctx, arg):
        res = None
        if isinstance(arg, Expression):
            res = arg.eval(ctx)

        if res is None:
            raise PseudoRuntimeError(self.context, "Invalid expression argument")

        return res

    @staticmethod
    def _normalise_arg(arg):
        if isinstance(arg, Token) and arg.type == 'identifier':
            arg = VariableReference(arg.value)

        elif isinstance(arg, Token) and arg.type in ('string', 'number'):
            arg = LiteralExpression(arg)

        elif not isinstance(arg, Expression):
            raise TypeError("Expression must contain either strings, numbers, identifiers or other expressions.")

        return arg

class VariableReference(Expression):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def eval(self, ctx):
        res = ctx.get_var(self.name)
        if res is None:
            raise PseudoNameError(self.context, "{} is undefined".format(self.name))

        return res

    def set(self, ctx, value):
        ctx.set_var(self.name, value)

class LiteralExpression(Expression):
    def __init__(self, token):
        self.token = token

    @property
    def type(self):
        return self.token.type

    @property
    def value(self):
        return self.token.value

    def eval(self, ctx):
        return self.token

class UnaryExpression(Expression):
    def __init__(self, op, arg):
        super().__init__()
        self.operation = op.value

        self.argument = Expression._normalise_arg(arg)

    def _do_operation(self, ctx, op_type, func):
        arg = Expression._get_arg(ctx, self.argument)

        if arg.type == op_type:
            return Token(op_type, func(arg.value))

        return None

    def eval(self, ctx):

        res = None
        if self.operation in NEG_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda x: -x)

        elif self.operation in PLUS_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda x: +x)

        elif self.operation in NOT_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda x: not x)

        if res is None:
            arg_type = Expression._get_arg(ctx, self.argument).type

            raise PseudoTypeError(self.context, "{}({}) not supported".format(self.operation, arg_type))

        return res

class BinaryExpression(Expression):
    def __init__(self, op, arg1, arg2):
        super().__init__()
        self.operation = op.value

        self.argument1 = Expression._normalise_arg(arg1)
        self.argument2 = Expression._normalise_arg(arg2)

    def _do_operation(self, ctx, op_type, func):
        arg1 = Expression._get_arg(ctx, self.argument1)
        arg2 = Expression._get_arg(ctx, self.argument2)

        if arg1.type == arg2.type == op_type:
            return Token(op_type, func(arg1.value, arg2.value))

        return None

    def eval(self, ctx):
        #print("Eval with op {}:".format(self.operation))
        #print("Arg1: {}".format(self.argument1))
        #print("Arg2: {}".format(self.argument2))
        res = None
        if self.operation in ADD_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: a + b)
            if not res: res = self._do_operation(ctx, 'string', lambda a,b: a + b)

        elif self.operation in SUB_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: a - b)

        elif self.operation in MUL_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: a * b)

        elif self.operation in DIV_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: a / b)

        elif self.operation in EQ_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: int(a == b))

        elif self.operation in LT_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: int(a < b))

        elif self.operation in GT_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: int(a > b))

        elif self.operation in LE_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: int(a <= b))

        elif self.operation in GE_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: int(a >= b))

        if res is None:
            arg1_type = Expression._get_arg(ctx, self.argument1).type
            arg2_type = Expression._get_arg(ctx, self.argument2).type

            raise PseudoTypeError(self.context, "{} {} {} not supported".format(arg1_type, self.operation, arg2_type))

        return res


class KeywordExpression(Expression):
    def __init__(self, keyword, *args):
        self.keyword = keyword.value
        self.arguments = list(map(Expression._normalise_arg, args))

    def eval(self, ctx):
        if self.keyword in ('OUTPUT', 'PRINT'):
            for arg in self.arguments:
                arg = Expression._get_arg(ctx, arg)
                print(arg.value, end=' ')
            print("", end='\n')

        elif self.keyword == 'INPUT':
            target = self.arguments[0]

            if not isinstance(target, VariableReference):
                raise PseudoTypeError(self.context, "Input target not a variable reference")

            value = input("{}: ".format(target.name))
            try:
                value = Token('number', float(value))
            except ValueError:
                value = Token('string', value)

            target.set(ctx, value)

            