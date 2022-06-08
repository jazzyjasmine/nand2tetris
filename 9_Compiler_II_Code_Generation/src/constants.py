SYMBOLS = {
    '{', '}', '(', ')', '[', ']', '.',
    ',', ';', '+', '-', '*', '/', '&',
    '|', '<', '>', '=', '~'
}

SPECIAL_SYMBOL_TO_TOKEN = {
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    '&': '&amp;'
}

FIELD = 'field'
STATIC = 'static'
TRUE = 'true'
FALSE = 'false'
NULL = 'null'
THIS = 'this'

KEYWORDS = {
    'class', 'constructor', 'function',
    'method', FIELD, STATIC,
    'var', 'int', 'char',
    'boolean', 'void', TRUE,
    FALSE, NULL, THIS,
    'let', 'do', 'if',
    'else', 'while', 'return'
}

KEYWORD_CONSTANTS = {
    TRUE, FALSE, NULL, THIS
}

# segment
CONSTANT = 'constant'
ARGUMENT = 'argument'
LOCAL = 'local'
THIS = 'this'
THAT = 'that'
POINTER = 'pointer'
TEMP = 'temp'
STATIC = 'static'

SEGMENTS = {
    CONSTANT, ARGUMENT, LOCAL, THIS, THAT, POINTER, TEMP, STATIC
}

# command
ADD = 'add'
SUB = 'sub'
NEG = 'neg'
EQ = 'eq'
GT = 'gt'
LT = 'lt'
AND = 'and'
OR = 'or'
NOT = 'not'
MULTIPLY = 'call Math.multiply 2'
DIVIDE = 'call Math.divide 2'

COMMANDS = {
    ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT,
    MULTIPLY, DIVIDE
}

OPERATORS_TO_COMMANDS = {
    '+': ADD,
    '-': SUB,
    '=': EQ,
    '>': GT,
    '<': LT,
    '&': AND,
    '|': OR,
    '*': MULTIPLY,
    '/': DIVIDE,
}

UNARIES_TO_COMMANDS = {
    '-': NEG,
    '~': NOT,
}

# KINDS
NONE = 'none'
KINDS = {ARGUMENT, LOCAL, FIELD, STATIC, NONE}
