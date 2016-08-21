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

    def child_context(self):
        new_ctx = Context()
        new_ctx.modules = self.modules
        new_ctx.programs = self.programs
        return new_ctx

    def get_var(self, name):
        return self.variables.get(name)

    def set_var(self, name, value, ctx=None):
        if name in DEFAULT_CONSTANTS:
            raise PseudoRuntimeError(ctx, "Cannot reassign pre-defined variable {}".format(name))

        self.variables[name] = value

    def get_module(self, name):
        return self.modules.get(name)

    def def_module(self, name, mod, ctx=None):
        if name not in self.modules:
            self.modules[name] = mod

        else:
            raise PseudoRuntimeError(ctx, "Module {} already defined".format(name))

    def get_program(self, name):
        return self.programs.get(name)

    def def_program(self, name, prog, ctx=None):
        if name not in self.programs:
            self.programs[name] = prog

        else:
            raise PseudoRuntimeError(ctx, "Program {} already defined".format(name))