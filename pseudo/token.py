#!/usr/bin/env python3

import re
from collections import namedtuple
from contextlib import contextmanager

WHITESPACE_RE = re.compile(r'[ \r\n\v\t]+')
IDENTIFIER_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
NUMBER_RE = re.compile(r'[0-9]+|[0-9]*\.[0-9]+')
STRING_RE = re.compile(r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')
ENDLINE_RE = re.compile(r'(;|\r?\n)')
OPERATOR_RE = re.compile(r'(==|<-|<=|>=|!=|n?eq|and|or|[!+\-*/<>=])')
NONE_RE = re.compile(r'\x00')
ANY_RE = re.compile(r'[^\x00]*')

NEG_OPERATORS = ('-',)
PLUS_OPERATORS = ('+',)
NOT_OPERATORS = ('!', 'not')
UNARY_OPERATORS = NEG_OPERATORS + PLUS_OPERATORS + NOT_OPERATORS

ADD_OPERATORS = ('+',)
SUB_OPERATORS = ('-',)
MUL_OPERATORS = ('*',)
DIV_OPERATORS = ('/',)

EQ_OPERATORS = ('=', '==', 'eq', 'equals')
NEQ_OPERATORS = ('!=', 'neq')

LT_OPERATORS = ('<', 'lt')
GT_OPERATORS = ('>', 'gt')
LE_OPERATORS = ('<=', 'le')
GE_OPERATORS = ('>=', 'ge')

BINARY_AND_OPERATORS = ('&',)
BINARY_OR_OPERATORS = ('|',)
BINARY_XOR_OPERATORS = ('^',)

AND_OPERATORS = ('&&', 'and')
OR_OPERATORS = ('||', 'or')

ASSIGN_OPERATORS = (':=', '=', '<-')

KEYWORDS = "BEGIN", "END", "FOR", "TO", "WHILE", "THEN", "MODULE", "PROGRAM", "IF", "ELSE", "DO", "NEXT", "REPEAT", "OUTPUT", "INPUT", "PRINT"

class ParseError(Exception):
    def __init__(self, ctx, msg):
        msg = ctx.get_context() + msg
        super().__init__(msg)

class ParseExpected(ParseError):
    def __init__(self, ctx, expected, got=None):
        msg = "Expected {}".format(expected)

        if isinstance(got, Token):
            got = "{} '{}'".format(got.type, got.value)

        if got is not None:
            msg += ", got {}".format(got)

        super().__init__(ctx, msg)

class PseudoRuntimeError(Exception):
    def __init__(self, ctx, msg):
        msg = ctx + msg
        super().__init__(msg)

class PseudoTypeError(PseudoRuntimeError):
    pass

class PseudoNameError(PseudoRuntimeError):
    pass

class PseudoFlowControl(Exception):
    pass

class PseudoBreak(PseudoFlowControl):
    pass

class PseudoContinue(PseudoFlowControl):
    pass

Token = namedtuple('Token', "type, value")

class Tokeniser:
    def __init__(self, name):
        self.lines = []
        self.row = 1
        self.col = 1
        self.level = 1
        self.name = name
        self.tokeniser = iter(self)
        self._peek = None
        self._peek_token = None
        self._ready_ctx = []

    def reset(self):
        self.lines = []
        self.row = 1
        self.col = 1
        self.level = 1
        self._peek = None
        self._peek_token = None

    @contextmanager
    def nest(self):
        self.level += 1

        yield

        self.level -= 1

    @contextmanager
    def ready_context(self):
        idx = len(self._ready_ctx)
        self._ready_ctx.append(self.get_context())

        yield

        while len(self._ready_ctx) > idx:
            self._ready_ctx.pop()

    def get_context(self):
        if len(self._ready_ctx) > 0:
            return self._ready_ctx.pop()

        ctx  = ""
        row = self.row
        col = self.col

        if row > len(self.lines):
            row = self.row-1
            col = len(self.lines[row-1])

        if row < 1:
            return "File {}: \n".format(self.name)

        elif col < 1:
            return "File {}, line {}: \n".format(self.name, row)

        ctx += "File {}, line {}, column {}: \n".format(self.name, row, col)
        ctx += self.lines[row-1] + "\n"
        ctx += "{}^\n".format(' ' * (col-1))
        return ctx

    def peek(self):
        if self._peek is not None:
            return self._peek

        self._peek = self._get_char()
        return self._peek

    def char(self):
        if self._peek is not None:
            res = self._peek
            self._peek = None
            return res

        else:
            return self._get_char()

    def consume(self, until_re=None, while_re=None):
        #print("Consuming...")
        res = self.char()
        until_cond = lambda x: False if not until_re else until_re.match(x)
        while_cond = lambda x: True  if not while_re else while_re.fullmatch(x)

        nchar = None
        while while_cond(res):
            if until_cond(res):
                break

            nchar = self.char()
            if not nchar:
                return res

            res += nchar

        #print("Consumption complete: '{}'".format(res))

        if nchar:
            self._peek = nchar

        return res[:-1]

    def __iter__(self):
        c = self.peek()
        while c:

            if ENDLINE_RE.match(c):
                self.char()
                #self.consume(while_re=ENDLINE_RE)
                yield Token('eol', '')

            elif WHITESPACE_RE.match(c):
                self.consume(while_re=WHITESPACE_RE)

            elif c in ('"', "'"):
                string = str(self.consume(until_re=STRING_RE)[1:])
                self.char() # consume end of string
                yield Token('string', string)

            elif NUMBER_RE.match(c):
                num = self.consume(while_re=NUMBER_RE)
                yield Token('number', float(num))

            elif OPERATOR_RE.match(c):
                yield Token('operator', self.consume(while_re=OPERATOR_RE))

            elif IDENTIFIER_RE.match(c):
                ident = self.consume(while_re=IDENTIFIER_RE)
                if ident.upper() in KEYWORDS:
                    yield Token('keyword', ident)
                else:
                    yield Token('identifier', ident)

            else:
                yield Token('symbol', self.char())

            c = self.peek()

        yield Token('eol', '')

    def peek_token(self):
        try:
            if self._peek_token is not None:
                return self._peek_token

            self._peek_token = next(self.tokeniser)
            #print("new token: {}, '{}'".format(self._peek_token.type, self._peek_token.value))
            return self._peek_token

        except StopIteration as e:
            raise EOFError from e

    def token(self):
        try:
            if self._peek_token is not None:
                token = self._peek_token
                self._peek_token = None
                return token
            else:
                res = next(self.tokeniser)
                #print("new token: {}, '{}'".format(res.type, res.value))
                return res

        except StopIteration as e:
            raise EOFError from e

class FileTokeniser(Tokeniser):
    def __init__(self, fp, filename='<stream>'):
        super().__init__(filename)
        self.fp = fp
        self.lines = re.compile(r'\r?\n').split(fp.read())

    def _get_char(self):
        if self.row > len(self.lines):
            return None

        line = self.lines[self.row-1]
        if self.col > len(line):
            self.row += 1
            self.col = 1
            return '\n'

        c = line[self.col-1]
        self.col += 1
        return c

class REPLTokeniser(Tokeniser):
    def __init__(self):
        super().__init__("<repl>")

    def _get_char(self):
        while self.row > len(self.lines):
            prompt = ">>> "
            if self.level >= 2:
                prompt = "{}... ".format("...." * (self.level - 2))

            line = input(prompt)
            self.lines.append(line)

        line = self.lines[self.row-1]
        if self.col > len(line):
            self.row += 1
            self.col = 1
            return '\n'

        c = line[self.col-1]
        self.col += 1
        return c