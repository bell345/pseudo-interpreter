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
            raise PseudoRuntimeError(None, "Invalid expression argument")

        return res

    @staticmethod
    def _normalise_arg(arg):
        if isinstance(arg, Token) and arg.type == 'identifier':
            arg = VariableReference(arg.value)

        elif isinstance(arg, Token) and arg.type in ('string', 'number'):
            arg = LiteralExpression(arg)

        elif isinstance(arg, Token) and arg.type == 'keyword':
            arg = KeywordReference(arg.value)

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
        ctx.set_var(self.name, value, self.context)

class ModuleReference(Expression):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

    def eval(self, ctx):
        res = ctx.get_module(self.name)
        if res is None:
            raise PseudoNameError(self.context, "Module {} is undefined or is not a module".format(self.name))

        return res.call(ctx, self.args)

class KeywordReference(Expression):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def eval(self, ctx):
        raise PseudoNameError(self.context, "{} cannot be used as a variable reference".format(self.name))

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
            res = func(arg.value)
            if isinstance(res, str):
                return Token('string', res)
            else:
                return Token('number', res)

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
        if isinstance(op_type, str):
            op_type = (op_type,)

        arg1 = Expression._get_arg(ctx, self.argument1)
        arg2 = Expression._get_arg(ctx, self.argument2)

        if arg1.type != arg2.type:
            return None

        if arg1.type not in op_type:
            return None

        res = func(arg1.value, arg2.value)
        if isinstance(res, str):
            return Token('string', res)
        elif res is None:
            return Token('symbol', None)
        else:
            return Token('number', res)

    def eval(self, ctx):
        #print("Eval with op {}:".format(self.operation))
        #print("Arg1: {}".format(self.argument1))
        #print("Arg2: {}".format(self.argument2))
        res = None
        if self.operation in ADD_OPERATORS:
            res = self._do_operation(ctx, ('number', 'string'), lambda a,b: a + b)

        elif self.operation in SUB_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: a - b)

        elif self.operation in MUL_OPERATORS:
            res = self._do_operation(ctx, 'number', lambda a,b: a * b)

        elif self.operation in DIV_OPERATORS:
            try:
                res = self._do_operation(ctx, 'number', lambda a,b: a / b)
            except ZeroDivisionError as e:
                raise PseudoRuntimeError(self.context, 'Cannot divide by zero')

        elif self.operation in EQ_OPERATORS:
            res = self._do_operation(ctx, ('number', 'string', 'symbol'), lambda a,b: int(a == b))

        elif self.operation in NEQ_OPERATORS:
            res = self._do_operation(ctx, ('number', 'string', 'symbol'), lambda a,b: int(a != b))

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
        res = Token('symbol', None)
        if self.keyword == "RUN":
            prog_name = self.arguments[0]

            if not isinstance(prog_name, VariableReference):
                raise PseudoTypeError(self.context, "Run target not a program reference")

            prog = ctx.get_program(prog_name.name)
            if not prog:
                raise PseudoNameError(self.context,
                        "Program {} is not defined or is not a program".format(prog_name.name))

            res = prog.eval(ctx)

        elif self.keyword in ('OUTPUT', 'PRINT'):
            for arg in self.arguments:
                arg = Expression._get_arg(ctx, arg)
                print(arg.value, end=' ')
            print("", end='\n')

        elif self.keyword == 'INPUT':
            type_ = None
            type_kw = self.arguments[0]
            target = self.arguments[1]

            if isinstance(type_kw, KeywordReference):
                if type_kw.name in ('NUMBER', 'INTEGER', 'INT', 'FLOAT', 'REAL', 'STRING'):
                    type_ = type_kw.name

            if not isinstance(target, VariableReference):
                raise PseudoTypeError(self.context, "Input target not a variable reference")

            prompt = "{}{}: ".format(target.name,
                    " ({})".format(type_.lower()) if type_ else "")

            value = input(prompt)
            if type_ in ('NUMBER', 'FLOAT', 'REAL'):
                while True:
                    try:
                        value = Token('number', float(value))
                        break
                    except ValueError:
                        print("Please enter a number.")
                        value = input(prompt)

            elif type_ in ('INTEGER', 'INT'):
                while True:
                    try:
                        value = Token('number', int(value))
                        break
                    except ValueError:
                        print("Please enter an integer.")
                        value = input(prompt)

            elif type_ in ('STRING',):
                value = Token('string', value)

            else:
                try:
                    value = Token('number', float(value))
                except ValueError:
                    value = Token('string', value)

            target.set(ctx, value)
            res = value

        return res

            