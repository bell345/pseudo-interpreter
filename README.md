# pseudo-interpreter

An interpreter for simple PASCAL-like pseudo code.
The pseudo language has been defined to be both easy to learn and its syntax very forgiving for newcomers.
That being said, this interpreter does not do anything that the programmer does not intend, like implicit casting.

## Features

* REPL shell for program input
* Forgiving, PASCAL-like syntax
* Error handling and reporting
* Designed to complement educational materials

## Usage

From the repository root, run:

    python3 -m pseudo [file_name]

If run without a file name, you will be introduced into an interactive shell where you can directly input programs.

## Syntax

_NOTE_: Only basic expressions, selections and iterations have been implemented. Further changes could be implemented at any time.

### Notes on the Meta-Syntax Notation

I originally attempted to mimic [Backus-Naur Form](https://en.wikipedia.org/wiki/Backus-Naur_Form), while at the same time extending some functionality.
A reference:

    > xyz <         = the character/sequence 'xyz'
    'xyz'           = the character/sequence 'xyz'
    a : b c ;       = a is defined as b followed by c, where b and c are separated by whitespace
    stmt1 | stmt2   = stmt1 or stmt2
    ['a' - 'z']     = any character between 'a' and 'z', including 'a' and 'z'
    [statement]*    = statement 0, 1 or more times
    [statement]+    = statement at least once
    statement?      = optional statement

The basic units of syntax are as follows:

    digit           : ['0' - '9']
                    ;

    letter          : ['A' - 'Z'] | ['a' - 'z']
                    ;

    hex_letter      : ['A' - 'F'] | ['a' - 'f'] | ['0' - '9']
                    ;

    ident_begin     : letter | '_'
                    ;

    ident_symbol    : ident_begin | ['0' - '9']
                    ;

    identifier      : ident_begin [ident_symbol]*
                    ;

    string_char     : (any character not including > \ <, > " < or > ' < )
                    | '\r' | '\n'
                    | '\x' hex_letter hex_letter
                    | '\u' hex_letter hex_letter hex_letter hex_letter
                    | > \\ <
                    | > \' <
                    | > \" <
                    ;

    string          : > " < [string_char]* > " <
                    | > ' < [string_char]* > ' <
                    ;

    number          : [digit]* ['.']? [digit]+
                    ;

All programs start with a PROGRAM declaration, followed by a statment list:

    program         : program_decl begin_stmt [statement]* end_stmt
                    ;

    program_decl    : 'PROGRAM' identifier stmt_end
                    ;

    begin_stmt      : 'BEGIN' stmt_end
                    ;

    stmt_end        : ';'
                    | '\r\n'
                    | '\n'
                    ;

    end_stmt        : 'END' stmt_end
                    | 'END' identifier stmt_end
                    ;

Modules are reusable blocks of code that can return different values based upon a set of parameters.
_NOTE_: Modules cannot yet be called.

    module          : module_decl [param_decl]* begin_stmt [statement]* end_stmt
                    ;

    param_decl      : 'PARAM' identifier stmt_end
                    ;

Statments can be either assignment, selection, iteration, jump or I/O statments:

    statement       : assignment_stmt stmt_end
                    | selection_stmt stmt_end
                    | iteration_stmt stmt_end
                    | jump_stmt stmt_end
                    | io_stmt stmt_end
                    ;

Assignment statements assign a value to a variable.
If a variable is referenced without being assigned a value, an error will be raised.

    assigment_stmt  : identifier assignment_op expression
                    ;

    assignment_op   : '<-'
                    | ':='
                    | '='
                    ;

Selection statements conditionally execute other statements based upon a expression.

    selection_stmt  : if_stmt [statement]* end_stmt
                    | if_stmt [statement]* else_stmt [statement]* end_stmt
                    ;

    if_stmt         : 'IF' expression then_kw? stmt_end
                    ;

    else_stmt       : 'ELSE' stmt_end
                    ;

    then_kw         : 'THEN'
                    | 'DO'
                    ;

Iteration statements execute the same set of statements over and over conditionally or for a certain number of times.

    iteration_stmt  : while_stmt [statement]* repeat_stmt
                    | for_stmt [statement]* repeat_stmt
                    ;

    while_stmt      : 'WHILE' expression then_kw? stmt_end
                    ;

    for_stmt        : 'FOR' assignent_stmt 'TO' expression then_kw? stmt_end
                    ;

    repeat_stmt     : 'REPEAT' stmt_end
                    | 'NEXT' stmt_end
                    | end_stmt
                    ;

Jump statements change the control flow unconditionally and can be used to terminate iteration loops prematurely.
_NOTE_: Not implemented yet.

    jump_stmt       : 'BREAK' | 'CONTINUE'
                    ;

I/O statements are the methods of input and output that pseudo programs have available to them.

    io_stmt         : 'INPUT' identifier
                    | 'OUTPUT' expression
                    ;

Expressions are very similar to those in C, including the same operators and identical order of operations.
I've decided not to recreate the C syntax here, as it's (mostly) intutive and similar to how ordinary math works.
There are a few differences:

* Ternary operators have not been implemented.
* There are various synonyms for the operators, including text keywords:
    * `equality_op      : '=' | '==' | 'eq' ;`
    * `non_equality_op  : '!=' | 'neq' ;`
    * `lt_operator      : '<' | 'lt' ;`
    * `gt_operator      : '>' | 'gt' ;`
    * `le_operator      : '<=' | 'le' ;`
    * `ge_operator      : '>=' | 'ge' ;`
    * `logical_and_op   : '&&' | 'and' ;`
    * `logical_or_op    : '||' | 'or' ;`
    * `unary_not_op     : '!' | 'not' ;`
* Assignments cannot be present in expressions.
* The comma operator has not been implemented.

## Basic Examples

Print the maximum of 3 input numbers:

    PROGRAM PrintBiggestNumber
    BEGIN
        entered_number <- 0
        biggest_number <- 0
        FOR count = 1 TO 3
            INPUT entered_number
            IF entered_number > biggest_number THEN
                biggest_number = entered_number
            END IF
        NEXT
        OUTPUT biggest_number
    END

## Planned Improvements

* Casting numbers to strings and vice versa
* More iteration types (test-last)
* Function support
* Module/import support

(C) Thomas Bell 2016, MIT License.

    