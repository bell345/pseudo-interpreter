#!/usr/bin/env python3

import re
from collections import namedtuple
from contextlib import contextmanager

WHITESPACE_RE = re.compile(r'[ \r\n\v\t]+')
IDENTIFIER_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
NUMBER_RE = re.compile(r'[0-9]+|[0-9]+\.[0-9]*|[0-9]*\.[0-9]+')
STRING_RE = re.compile(r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')
ENDLINE_RE = re.compile(r'(;|\r?\n)')
OPERATOR_RE = re.compile(r'(==|<-|<=|>=|!=|n?eq|and|or|[!+\-*/<>=])')
NONE_RE = re.compile(r'\x00')
ANY_RE = re.compile(r'[^\x00]*')
COMMENT_RE = re.compile(r'#.*')

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

KEYWORDS = "BEGIN", "END", "FOR", "TO", "WHILE", "THEN", "MODULE", "PROGRAM", "IF", "ELSE", "DO", "NEXT", "REPEAT", "OUTPUT", "INPUT", "PRINT", "BREAK", "CONTINUE", "RETURN", "RUN", "IS", "NOT", "INTEGER", "FLOAT", "REAL", "STRING", "INT", "NUMBER", "PARAM"

class ParseError(Exception):
    def __init__(self, ctx, msg):
        msg = ctx.get_context()[0] + msg
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
        if ctx:
            msg = ctx + msg
        super().__init__(msg)

class PseudoTypeError(PseudoRuntimeError):
    pass

class PseudoNameError(PseudoRuntimeError):
    pass

class PseudoFlowControl(Exception):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.context = ctx

class PseudoBreak(PseudoFlowControl):
    pass

class PseudoContinue(PseudoFlowControl):
    pass

class PseudoReturn(PseudoFlowControl):
    def __init__(self, ctx, ret):
        super().__init__(ctx)
        self.value = ret

Token = namedtuple('Token', "type, value")
def keyword_eq(token1, token2):
    if not isinstance(token1, Token) or not isinstance(token2, Token):
        return False

    if not (token1.type == token2.type == 'keyword'):
        return token1 == token2

    return token1.value.upper() == token2.value.upper()

class Tokeniser:
    def __init__(self, name):
        self.name = name
        self.reset()

    def reset(self):
        self.lines = []
        self.row = 1
        self.col = 1
        self.level = 1
        self.tokeniser = iter(self)
        self._peek = None
        self._peek_token = None
        self._peek_token_row_col = None
        self._ready_ctx = []

    @contextmanager
    def nest(self):
        self.level += 1

        yield

        self.level -= 1

    @contextmanager
    def ready_context(self, ctx=None):
        if not ctx:
            ctx = self.raw_context()

        idx = len(self._ready_ctx)
        self._ready_ctx.append(ctx)

        yield ctx

        while len(self._ready_ctx) > idx:
            self._ready_ctx.pop()

    def raw_context(self):
        if self._peek_token_row_col is not None:
            return self._peek_token_row_col

        return self.row, self.col

    def get_context(self):
        ctx = ""

        if len(self._ready_ctx) > 0:
            row, col = self._ready_ctx.pop()
        else:
            row, col = self.raw_context()

        if row > len(self.lines):
            row = row-1
            col = len(self.lines[row-1])+1

        if row < 1:
            return "File {}: \n".format(self.name)

        elif col < 1:
            return "File {}, line {}: \n".format(self.name, row)

        ctx += "File {}, line {}, column {}: \n".format(self.name, row, col)
        ctx += self.lines[row-1] + "\n"
        ctx += "{}^\n".format(' ' * (col-1))
        return ctx, (row, col)

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

    def _parse_string_escapes(self, string):
        i = 0
        res = ""
        escapes = { 'r': '\r', 'n': '\n', "'": "'", '"': '"', '\\': '\\' }
        try:
            while i < len(string):
                if string[i] == '\\' and (i+1) < len(string):
                    i += 1
                    c = string[i]
                    if c in escapes:
                        res += escapes[c]

                    elif c == 'x' and (i+2) < len(string):
                        res += chr(int(string[i+1 : i+3], 16))
                        i += 2

                    elif c == 'u' and (i+4) < len(string):
                        res += chr(int(string[i+1 : i+5], 16))
                        i += 4

                    else:
                        res += '\\' + c

                else:
                    res += string[i]

                i += 1

            return res

        except ValueError as e:
            raise ParseError(self, 'Invalid character escape')

    def __iter__(self):
        c = self.peek()
        while c:

            if COMMENT_RE.match(c):
                self.consume(while_re=COMMENT_RE)

            elif ENDLINE_RE.match(c):
                self.char()
                #self.consume(while_re=ENDLINE_RE)
                yield Token('eol', '')

            elif WHITESPACE_RE.match(c):
                self.consume(while_re=WHITESPACE_RE)

            elif c in ('"', "'"):
                string = self._parse_string_escapes(self.consume(until_re=STRING_RE)[1:])
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
                    yield Token('keyword', ident.upper())
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

            self._peek_token_row_col = self.raw_context()
            self._peek_token = next(self.tokeniser)
            #print("new token: {}, '{}'".format(self._peek_token.type, self._peek_token.value))
            return self._peek_token

        except StopIteration as e:
            raise EOFError from e

    def token(self):
        try:
            if self._peek_token is not None:
                token = self._peek_token
                self._peek_token = self._peek_token_row_col = None
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