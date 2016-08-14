#!/usr/bin/env python3

from .token import Token

PRE_DEFINED = {
    'TRUE': Token('number', 1),
    'true': Token('number', 1),
    'True': Token('number', 1),
    'FALSE': Token('number', 0),
    'false': Token('number', 1),
    'False': Token('number', 1),
    'NULL': Token('symbol', None),
    'null': Token('symbol', None),
    'None': Token('symbol', None),
    'inf': Token('number', float('inf')),
    'INF': Token('number', float('inf')),
    'Infinity': Token('number', float('inf'))
}

class Context:
    def __init__(self):
        self.variables = {}
        self.variables.update(PRE_DEFINED)

    def get_var(self, name):
        return self.variables.get(name)

    def set_var(self, name, value):
        self.variables[name] = value