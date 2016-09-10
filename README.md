# pseudo-interpreter

An interpreter for simple PASCAL-like pseudo code.
The pseudo language has been defined to be both easy to learn and its syntax
very forgiving for newcomers. That being said, this interpreter does not do
anything that the programmer does not intend, like implicit casting.

## Features

* REPL shell for program input
* Forgiving, PASCAL-like syntax
* Error handling and reporting
* Designed to complement educational materials

## Installation

From the repository root, run:

    pip3 install .

or the following to install as a user package (making sure to add ~/.local/bin/ to your $PATH):

    pip install . --user

## Usage

Syntax:

    pseudo [file_name] [--trace output_trace.txt]

If run without a file name, you will be introduced into an interactive shell
where you can directly input programs.

## Syntax

_NOTE_: Further changes could be implemented at any time.

### Notes on the Meta-Syntax Notation

I originally attempted to mimic
[Backus-Naur Form](https://en.wikipedia.org/wiki/Backus-Naur_Form),
while at the same time extending some functionality.

A reference:

    > xyz <         = the character/sequence 'xyz'
    'xyz'           = the character/sequence 'xyz'
    a : b c ;       = a is defined as b followed by c, where b and c are separated by whitespace
    stmt1 | stmt2   = stmt1 or stmt2
    ['a' - 'z']     = any character between 'a' and 'z', including 'a' and 'z'
    [statement]*    = statement 0, 1 or more times
    [statement]+    = statement at least once
    [statement]?    = optional statement

### Syntax Units

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

### Comments

Comments are sections of text which are ignored when parsing the file and can
be used to add inline documentation.

    comment         : '#' (any character)* '\n'
                    ;

### Programs

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

Programs are run in the REPL using RUN statements with the program name. In a
code file, if there is only one program present, that program will be run. If
there are multiple programs, the one named 'main' will be called. If there is
no program named 'main', an interactive prompt will ask you to specify which
program is to be run.

    run_stmt        : 'RUN' identifier stmt_end
                    ;

### Modules

Modules are reusable blocks of code that can return different values based upon
a set of parameters. Calling modules works similarly to C. Modules occupy a
different namespace than programs, so a module can be named the same as a
program.

To cast strings to numbers and numbers to strings, the modules `to_str` and
`to_num` are provided.

    module          : module_decl [param_decl]* begin_stmt [statement]* end_stmt
                    ;

    module_decl     : 'MODULE' identifier stmt_end
                    ;

    param_decl      : 'PARAM' identifier stmt_end
                    ;

    module_call     : identifier '(' argument_list ')'
                    | identifier '()'
                    ;

    argument_list   :

### Statements

Statments can be either assignment, selection, iteration, jump or I/O
statments, or an expression such as a module call:

    statement       : assignment_stmt stmt_end
                    | selection_stmt stmt_end
                    | iteration_stmt stmt_end
                    | jump_stmt stmt_end
                    | io_stmt stmt_end
                    | expression stmt_end
                    ;

### Assignment Statements

Assignment statements assign a value to a variable. If a variable is referenced
without being assigned a value, an error will be raised.

    assigment_stmt  : identifier assignment_op expression
                    ;

    assignment_op   : '<-'
                    | ':='
                    | '='
                    ;

### Selection Statements

Selection statements conditionally execute other statements based upon an
expression.

    selection_stmt  : if_stmt [statement]* end_stmt
                    | if_stmt [statement]* else_block end_stmt
                    ;

    if_stmt         : 'IF' expression [then_kw]? stmt_end
                    ;

    else_block      : 'ELSE' stmt_end [statement]*
                    | 'ELSE' if_stmt [statement]* [else_block]?
                    ;

    then_kw         : 'THEN'
                    | 'DO'
                    ;

### Iteration Statements

Iteration statements execute the same set of statements over and over
conditionally or for a certain number of times.

    iteration_stmt  : while_stmt [statement]* repeat_stmt
                    | for_stmt [statement]* repeat_stmt
                    ;

    while_stmt      : 'WHILE' expression [then_kw]? stmt_end
                    ;

    for_stmt        : 'FOR' assignent_stmt 'TO' expression [then_kw]? stmt_end
                    ;

    repeat_stmt     : 'REPEAT' stmt_end
                    | 'NEXT' stmt_end
                    | end_stmt
                    ;

### Jump Statements

Jump statements change the control flow unconditionally and can be used to
terminate iteration loops prematurely or return values from modules.

    jump_stmt       : 'BREAK' stmt_end
                    | 'CONTINUE' stmt_end
                    | 'RETURN' expression stmt_end
                    ;

### I/O Statements

I/O statements are the methods of input and output that pseudo programs have
available to them. An INPUT statement can also accept a type identifier, which
tries to get an input from the user that always has the specified type.

    io_stmt         : 'INPUT' [type_spec]? identifier
                    | 'OUTPUT' expression
                    ;

    type_spec       : 'NUMBER' | 'REAL' | 'FLOAT'
                    | 'INT' | 'INTEGER'
                    | 'STRING'
                    ;

### Expressions

Expressions are very similar to those in C, including the same operators and
identical order of operations. I've decided not to recreate the C syntax here,
as it's (mostly) intutive and similar to how ordinary math works. There are a
few differences:

* Assignments cannot be present in expressions.
* Ternary operators have not been implemented.
* The comma operator has not been implemented.
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

## Examples

Examples of (hopefully) valid pseudo-code programs that can be ran with the
interpreter are in the `test/` directory.

## Planned Improvements

* More iteration types (test-last)
* Import support

(C) Thomas Bell 2016, MIT License.

