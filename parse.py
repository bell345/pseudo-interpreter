#!/usr/bin/env python3

from token import Token, ParseExpected, UNARY_OPERATORS
from expr import UnaryExpression, BinaryExpression, KeywordExpression
from statement import IfStatement, ForStatement, WhileStatement
from program import PseudoProgram

def skip_eol(ctx):
    token = ctx.peek_token()
    while token == Token('eol', ''):
        ctx.token()
        token = ctx.peek_token()

def pseudo_program(ctx):
    skip_eol(ctx)

    token = ctx.token()
    if token == Token('keyword', 'PROGRAM'):
        ctx.token()
        ident = ctx.token()
        if not ident or ident.value:
            raise ParseExpected(ctx, 'program name')
            
        ctx.nest()
        skip_eol(ctx)
        
        begin_kw = ctx.token()
        if begin_kw != Token('keyword', 'BEGIN'):
            raise ParseExpected(ctx, 'BEGIN')

        statements = statement_list(ctx)
        
        ctx.denest()
        return PseudoProgram(ident.value, statements)
        
    else:
        raise ParseExpected(ctx, 'PROGRAM')

def statement_list(ctx, end_kw='END', consume_end=True):
    if isinstance(end_kw, str):
        end_kw = (end_kw,)

    def check_end():
        skip_eol(ctx)
        
        token = ctx.peek_token()
        if token == Token('keyword', 'END'):
            if consume_end:
                ctx.token()
                # treat END, END IF, END WHILE equally
                qual = ctx.peek_token()
                if qual.type == 'keyword':
                    ctx.token()
                
            return True
        
        elif token.type == 'keyword' and token.value in end_kw:
            if consume_end:
                ctx.token()
                
            return True
    
    ctx.nest()
    statements = []
    while not check_end():
        stmt = statement(ctx)
        if not stmt:
            raise ParseExpected(ctx, 'statement')
        statements.append(stmt)
        
    ctx.denest()
    return statements

def statement(ctx):
    skip_eol(ctx)
    
    res = assignment_expr(ctx)
    if not res: res = selection(ctx)
    if not res: res = iteration(ctx)
    if not res: res = jump(ctx)
    if not res: res = io_statement(ctx)
    
    eol = ctx.token()
    if eol != Token('eol', ''):
        raise ParseExpected(ctx, 'end of statement')
    else:
        pass
        #print("A statement has been born: {}".format(
        #    type(res).__name__
        #))

    return res
    
def selection(ctx):
    if_kw = ctx.peek_token()
    if if_kw == Token('keyword', 'IF'):
        ctx.token()
        
        cond = conditional_expr(ctx)
        if not cond:
            raise ParseExpected(ctx, 'conditional')
            
        then_kw = ctx.peek_token()
        if then_kw.type == 'keyword' and then_kw.value in ('THEN', 'DO'):
            ctx.token() # consume peek
        
        stmt_list = statement_list(ctx, end_kw=('END', 'ELSE'), consume_end=False)
        else_list = []
        
        else_kw = ctx.peek_token()
        if else_kw == Token('keyword', 'ELSE'):
            ctx.token() # consume peek
            else_list = statement_list(ctx)

        return IfStatement(cond, stmt_list, else_list)
    
def iteration(ctx):
    iter_kw = ctx.peek_token()
    if iter_kw == Token('keyword', 'WHILE'):
        ctx.token() # consume peek
        
        while_cond = conditional_expr(ctx)
        if not cond:
            raise ParseExpected(ctx, 'conditional')
            
        then_kw = ctx.peek_token()
        if then_kw.type == 'keyword' and then_kw.value in ('THEN', 'DO'):
            ctx.token()
            
        stmt_list = statement_list(ctx, end_kw='REPEAT')
        
        return WhileStatement(while_cond, stmt_list)
        
    elif iter_kw == Token('keyword', 'FOR'):
        ctx.token() # consume peek
        
        start_expr = assignment_expr(ctx)
        if not start_expr:
            raise ParseExpected(ctx, 'assignment')
            
        to_kw = ctx.token()
        if to_kw != Token('keyword', 'TO'):
            raise ParseExpected(ctx, 'TO')
            
        end_expr = conditional_expr(ctx)
        if not end_expr:
            raise ParseExpected(ctx, 'expression')
            
        then_kw = ctx.peek_token()
        if then_kw.type == 'keyword' and then_kw.value in ('THEN', 'DO'):
            ctx.token()
            
        stmt_list = statement_list(ctx, end_kw='NEXT')
        
        return ForStatement(start_expr, end_expr, stmt_list)
        
def jump(ctx):
    jump_kw = ctx.peek_token()
    
def io_statement(ctx):
    io_kw = ctx.peek_token()
    if io_kw == Token('keyword', 'INPUT'):
        ctx.token()
        
        ref = expression(ctx)
        if ref.type != 'identifier':
            raise ParseExpected(ctx, 'identifier')
            
        return KeywordExpression(io_kw, ref).assoc(ctx)
        
    elif io_kw.type == 'keyword' and io_kw.value in ('OUTPUT', 'PRINT'):
        ctx.token()
        
        expr = expression(ctx)
        if not expr:
            raise ParseExpected(ctx, 'expression')
            
        return KeywordExpression(io_kw, expr).assoc(ctx)
    
def assignment_expr(ctx):
    target = ctx.peek_token()
    if target.type == 'identifier':
        ctx.token()
        
        op = ctx.token()
        if op.type != 'operator' or op.value not in ('=', '<-', ':='):
            raise ParseExpected(ctx, 'assignment operator', op)
        
        inner = expression(ctx)
        if not inner:
            raise ParseExpected(ctx, 'expression')
            
        return BinaryExpression(Token('operator', '<-'), target, inner).assoc(ctx)
        
def expression(ctx):
    return conditional_expr(ctx)
    
def conditional_expr(ctx):
    res = or_expr(ctx)
    if res: return res
    
    raise ParseExpected(ctx, 'conditional')

def unary_expr(ctx):
    op = ctx.peek_token()
    if op.type != 'operator' or op.value not in UNARY_OPERATORS:
        return primary_expr(ctx)
    ctx.token()
    
    arg = unary_expr(ctx)
    if not arg:
        raise ParseExpected(ctx, 'expression')

    return UnaryExpression(op, arg)
    
def primary_expr(ctx):
    res = ctx.token()
    #print("Got primary token: {}".format(res))
    if res.type in ('number', 'string', 'identifier'):
        return res

    elif res != Token('symbol', '('):
        raise ParseExpected(ctx, 'expression', res)
    
    res = expression(ctx)
    
    end_bracket = ctx.token()
    if end_bracket != Token('symbol', ')'):
        raise ParseExpected(ctx, "')'", end_bracket)
    
    return res
    
def _binary_expr(ops, _next_expr):
    def _curr_expr(ctx):
        arg1 = _next_expr(ctx)
        if not arg1:
            raise ParseExpected(ctx, 'expression')
            
        op = ctx.peek_token()
        #print("Peeked bexpr: {}".format(op))
        if op.value not in ops:
            return arg1
        ctx.token()
            
        arg2 = _curr_expr(ctx)
        if not arg2:
            raise ParseExpected(ctx, 'expression')
            
        return BinaryExpression(op, arg1, arg2)
        
    return _curr_expr

multiply_expr = _binary_expr(('*', '/'), unary_expr)
add_expr = _binary_expr(('+', '-'), multiply_expr)
relation_expr = _binary_expr(('<', '>', '<=', '>='), add_expr)
eq_expr = _binary_expr(('==', 'eq', 'equals', '!=' 'neq'), relation_expr)
binary_and_expr = _binary_expr(('&',), eq_expr)
binary_xor_expr = _binary_expr(('^',), binary_and_expr)
binary_or_expr = _binary_expr(('|',), binary_xor_expr)
and_expr = _binary_expr(('&&', 'and'), binary_or_expr)
or_expr = _binary_expr(('||', 'or'), and_expr)