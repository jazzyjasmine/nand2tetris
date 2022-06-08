from constants import *


class SymbolTable:
    def __init__(self):
        self.table = {}     # { var: (type, kind, index) }
        self.var_counts = {t : 0 for t in KINDS}


    def reset(self):
        self.table.clear()
        self.var_counts = {t : 0 for t in KINDS}


    def define(self, name, type_, kind):
        index = self.var_counts[kind]
        self.var_counts[kind] += 1
        self.table[name] = (type_, kind, index)


    def var_count(self, type_):
        return self.var_counts[type_]


    def kind_of(self, name):
        if name not in self.table:
            return NONE
        _, kind, _ = self.table[name]
        return kind


    def type_of(self, name):
        type_, _, _ = self.table[name]
        return type_


    def index_of(self, name):
        _, _, index = self.table[name]
        return index
