#!/usr/bin/env python3

from .token import Token, PseudoRuntimeError

DEFAULT_CONSTANTS = {
    'TRUE': Token('number', 1),
    'true': Token('number', 1),
    'True': Token('number', 1),
    'FALSE': Token('number', 0),
    'false': Token('number', 0),
    'False': Token('number', 0),
    'NULL': Token('symbol', None),
    'null': Token('symbol', None),
    'None': Token('symbol', None),
    'inf': Token('number', float('inf')),
    'INF': Token('number', float('inf')),
    'Infinity': Token('number', float('inf'))
}

class DefaultModules:

    @staticmethod
    def to_str(n): return str(n)
    @staticmethod
    def to_num(s):
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def upper(s): return s.upper()
    @staticmethod
    def lower(s): return s.lower()

    def modules():
        mods = {
            'to_str': DefaultModules.to_str,
            'to_num': DefaultModules.to_num,
            'upper': DefaultModules.upper,
            'lower': DefaultModules.lower
        }

        from .code import PseudoBinding
        return {name: PseudoBinding(name, f) for name,f in mods.items()}

class Context:
    def __init__(self):
        self.variables = {}
        self.variables.update(DEFAULT_CONSTANTS)

        self.modules = {}
        self.modules.update(DefaultModules.modules())

        self.programs = {}

    def child_context(self, name=None):
        new_ctx = Context()
        new_ctx.modules = self.modules
        new_ctx.programs = self.programs
        return new_ctx

    def get_var(self, name):
        return self.variables.get(name)

    def set_var(self, name, value, ctx=None, pos=None):
        if name in DEFAULT_CONSTANTS:
            raise PseudoRuntimeError(ctx, "Cannot reassign pre-defined variable {}".format(name))

        self.variables[name] = value

    def get_module(self, name):
        return self.modules.get(name)

    def def_module(self, name, mod, ctx=None, pos=None):
        if name not in self.modules:
            self.modules[name] = mod

        else:
            raise PseudoRuntimeError(ctx, "Module {} already defined".format(name))

    def get_program(self, name):
        return self.programs.get(name)

    def def_program(self, name, prog, ctx=None, pos=None):
        if name not in self.programs:
            self.programs[name] = prog

        else:
            raise PseudoRuntimeError(ctx, "Program {} already defined".format(name))

class TraceContext(Context):
    def __init__(self, name=None):
        super().__init__()
        self.assignments = []
        self.children = []
        self.name = name

    def child_context(self, name):
        new_ctx = TraceContext(name)
        new_ctx.programs = self.programs
        new_ctx.modules = self.modules
        self.children.append(new_ctx)
        return new_ctx

    def set_var(self, name, value, ctx=None, pos=None):
        super().set_var(name, value, ctx, pos)

        self.assignments.append((pos, name, value))

    def get_trace(self):

        from tabulate import tabulate

        res = ""
        if self.name:
            res += self.name + '\n'

        if self.assignments:
            vars = []
            for pos, name, value in self.assignments:
                if name not in vars:
                    vars.append(name)

            lines = []
            for pos, name, value in self.assignments:
                line = []
                row, col = pos
                line.append(row)
                for v in vars:
                    if v == name:
                        line.append(value.value)
                    else:
                        line.append(' ')

                lines.append(line)

            res += tabulate(lines, headers=(["Line"] + vars)) + '\n\n'

        for child in self.children:
            res += child.get_trace()

        return res
