import os
from constants import *
from symbol_table import SymbolTable
from vm_writer import VMWriter

########## GLOBAL VARIABLES ##########

elem_list = None    # all tokens
index = 0   # index on elem_list

class_name = "" # the class which is being compiled
subroutine_name = ""    # the subroutine which is being compiled
unique_marker = 0   # used to generate unique marker

class_symbol_table = SymbolTable()
subroutine_symbol_table = SymbolTable()

code_writer = None  # used to write .vm file
xml_writer = None   # used to write .xml file

######### PUBLIC METHODS ###############

def compile_class():
    class_symbol_table.reset()
    advance()   # class
    global class_name
    class_name = get_token_and_advance()
    global unique_marker
    unique_marker = 0   # start from 0 for every class
    advance()   # {

    while current_token() in ["static", "field"]:
        compile_class_var_dec()
    while current_token() in ["constructor", "function", "method"]:
        compile_subroutine_dec()

    advance()   # }


def compile_class_var_dec():
    kind = get_token_and_advance()  # static | field
    type_ = get_token_and_advance()  # type
    name = get_token_and_advance()   # varName
    class_symbol_table.define(name, type_, kind)   # fill symbol table
    while current_token() == ",":
        advance()   # ,
        name = get_token_and_advance()  # varName
        class_symbol_table.define(name, type_, kind)   # fill symbol table
    advance()   # ;


def compile_subroutine_dec():
    subroutine_symbol_table.reset()

    subroutine_type = get_token_and_advance()  # constructor | function | method
    if subroutine_type == "method":
        subroutine_symbol_table.define('this', class_name, ARGUMENT)

    get_token_and_advance()  # void | type
    global subroutine_name
    subroutine_name = get_token_and_advance()  # subroutineName
    advance()
    compile_parameter_list()
    advance()
    compile_subroutine_body(subroutine_type)


def compile_parameter_list():
    if current_token() == ")":
        return
    type_ = get_token_and_advance()  # type
    name = get_token_and_advance()  # varName
    subroutine_symbol_table.define(name, type_, ARGUMENT)
    while current_token() == ",":
        advance()
        type_ = get_token_and_advance()
        name = get_token_and_advance()
        subroutine_symbol_table.define(name, type_, ARGUMENT)
    return


def compile_subroutine_body(subroutine_type):
    advance()
    while current_token() == "var":
        compile_var_dec()
    n_vars = subroutine_symbol_table.var_count(LOCAL)
    code_writer.write_function(class_name + "." + subroutine_name, n_vars)
    # if the subroutine is a method, align THIS to its argument 0
    if subroutine_type == "method":
        code_writer.write_push(ARGUMENT, 0)
        code_writer.write_pop(POINTER, 0)
    # if it is a constructor
    elif subroutine_type == "constructor":
        n_fields = class_symbol_table.var_count(FIELD)
        code_writer.write_push(CONSTANT, n_fields)
        code_writer.write_call('Memory.alloc', 1)
        code_writer.write_pop(POINTER, 0)
    compile_statements()
    advance()


def compile_var_dec():
    advance()
    type_ = get_token_and_advance()
    name = get_token_and_advance()
    subroutine_symbol_table.define(name, type_, LOCAL)
    while current_token() == ",":
        advance()
        name = get_token_and_advance()
        subroutine_symbol_table.define(name, type_, LOCAL)
    advance()


def compile_statements():
    while current_token() in ["let", "if", "while", "do", "return"]:
        if current_token() == "let":
            compile_let()
        elif current_token() == "if":
            compile_if()
        elif current_token() == "while":
            compile_while()
        elif current_token() == "do":
            compile_do()
        else:
            compile_return()


def compile_let():
    advance()   # let
    var_name = get_token_and_advance()  # varName
    if current_token() == "[":  # left side is an array
        # var_name is an array name
        _, segment, index = lookup_var(var_name)
        code_writer.write_push(segment, index)  # push arr
        advance()
        compile_expression()    # put index(i.e. expression1) on stack
        advance()
        code_writer.write_arithmetic(ADD)   # arr + index
        advance()
        compile_expression()    # put value of expression2 on stack
        code_writer.write_pop(TEMP, 0)  # save expression2 to temp 0, and now arr + index on stack top
        code_writer.write_pop(POINTER, 1)   # THAT = arr + index
        code_writer.write_push(TEMP, 0) # put expression2 back on stack top
        code_writer.write_pop(THAT, 0)  # arr[index] = expression2

    else:   # no array on left side
        advance()
        compile_expression()    # put result on top of stack
        _, segment, index = lookup_var(var_name)
        code_writer.write_pop(segment, index)   # pop it to varName
    advance()


def compile_if():
    marker = generate_unique_marker()
    true_label = generate_label("IF_TRUE" + marker)
    false_label = generate_label("IF_FALSE" + marker)
    end_label = generate_label("IF_END" + marker)

    advance(2)
    compile_expression()
    code_writer.write_if(true_label)
    code_writer.write_goto(false_label)
    advance()
    code_writer.write_label(true_label)
    advance()
    compile_statements()    # execute statements if true
    advance()
    code_writer.write_goto(end_label)
    code_writer.write_label(false_label)    # start of else statement
    if current_token() == "else":
        advance(2)
        compile_statements()    # execute statements if false
        advance()
    code_writer.write_label(end_label)


def compile_while():
    marker = generate_unique_marker()
    while_start_label = generate_label("WHILE_START" + marker)
    while_continue_label = generate_label("WHILE_END" + marker)

    advance()
    code_writer.write_label(while_start_label)  # start of while
    advance()
    compile_expression()

    # if condition not met, break while loop
    code_writer.write_arithmetic(NOT)
    code_writer.write_if(while_continue_label)
    advance(2)
    compile_statements()
    code_writer.write_goto(while_start_label)

    advance()
    code_writer.write_label(while_continue_label)   # end of while


def compile_do():
    advance()   # do
    compile_expression()    # subroutineCall
    advance()   # ;

    code_writer.write_pop(TEMP, 0)


def compile_return():
    advance()   # return
    if current_token() != ";":
        compile_expression()
    else:   # return; -> return 0;
        code_writer.write_push(CONSTANT, 0)
    code_writer.write_return()
    advance()   # ;


def compile_expression():
    compile_term()
    while current_token() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
        symbol = get_token_and_advance()
        compile_term()
        command = OPERATORS_TO_COMMANDS[symbol]
        code_writer.write_arithmetic(command)


def compile_string():
    string = get_token_and_advance()[1:-1]
    length = len(string)
    code_writer.write_push(CONSTANT, length)
    code_writer.write_call("String.new", 1)
    for c in string:
        char = ord(c)   # 'P' -> 80
        code_writer.write_push(CONSTANT, char)
        code_writer.write_call("String.appendChar", 2)


def compile_unary_term():
    symbol = get_token_and_advance()
    compile_term()

    command = UNARIES_TO_COMMANDS[symbol]
    code_writer.write_arithmetic(command)


def compile_array_indexing():
    arr_name = get_token_and_advance()
    advance()   # [
    compile_expression()    # arr_index
    advance()   # ]

    _, segment, index = lookup_var(arr_name)
    code_writer.write_push(segment, index)  # push arr_name
    code_writer.write_arithmetic(ADD)   # arr_name + arr_index
    code_writer.write_pop(POINTER, 1)   # THAT = arr_name + arr_index
    code_writer.write_push(THAT, 0)  # push arr_name[arr_index]


def compile_subroutine_call_in_different_class():
    name = get_token_and_advance()  # className | varName
    subroutine_class_name = name
    type_, segment, index = lookup_var(name)
    n_args = 0  # number of actual arguments
    if type_ is not None: # name is varName
        subroutine_class_name = type_
        code_writer.write_push(segment, index)
        n_args += 1

    advance()   # .
    subroutine_name = get_token_and_advance()
    advance()
    n_args += compile_expression_list()
    advance()

    subroutine_fullname = subroutine_class_name + "." + subroutine_name
    code_writer.write_call(subroutine_fullname, n_args)


def compile_subroutine_call_in_same_class():
    subroutine_name = get_token_and_advance()
    advance()
    code_writer.write_push(POINTER, 0)  # push this == push pointer 0
    n_args = compile_expression_list()
    advance()

    subroutine_fullname = class_name + "." + subroutine_name
    code_writer.write_call(subroutine_fullname, n_args + 1)


def compile_subroutine_call():
    if next_token() == ".": # (varName | className ) . subroutineName ( expressionList )
        compile_subroutine_call_in_different_class()
    else:   # subroutinName ( expresionList )
        compile_subroutine_call_in_same_class()


def compile_term():
    if current_token().isnumeric():                     # Integer constant
        index = get_token_and_advance()
        code_writer.write_push(CONSTANT, index)
    elif current_token().startswith("\""):              # String constant
        compile_string()
    elif current_token() in KEYWORD_CONSTANTS:          # Keyword constant
        compile_keyword_constant()
    elif current_token() == "(":                        # ( expression )
        advance()
        compile_expression()
        advance()
    elif current_token() in ["~", "-"]:                 # unary term
        compile_unary_term()
    elif next_token() == "[":                           # varName [ expression ]
        compile_array_indexing()
    elif next_token() == "(" or next_token() == ".":    # subroutineCall
        compile_subroutine_call()
    else:                                               # varName
        name = get_token_and_advance()
        _, segment, index = lookup_var(name)
        code_writer.write_push(segment, index)


def compile_expression_list():
    expression_count = 0
    if current_token() == ")":
        return expression_count
    compile_expression()
    expression_count += 1
    while current_token() == ",":
        advance()
        compile_expression()
        expression_count += 1
    return expression_count


def compile_keyword_constant():
    """
    Compile and write keyword constant to .vm file.
    """
    keyword_constant = get_token_and_advance()
    if keyword_constant == 'false' or keyword_constant == 'null':
        code_writer.write_push(CONSTANT, 0)
    elif keyword_constant == 'true':
        code_writer.write_push(CONSTANT, 0)
        code_writer.write_arithmetic(NOT)
    elif keyword_constant == 'this':
        code_writer.write_push(POINTER, 0)
    else:
        raise Exception("unknow keyword constant")


############### HELPER METHODS #############

def current_token():
    """Get the current token."""
    if index >= len(elem_list):
        return ""
    return elem_list[index]


def advance(step=1):
    """Advance global index by step."""
    global index
    index += step


def get_token_and_advance():
    """Get current token and advance."""
    token = current_token()
    advance()
    return token


def next_token():
    """Get next token."""
    if index + 1 >= len(elem_list):
        raise Exception("No next token")
    return elem_list[index + 1]

def lookup_var(name):
    """
    Lookup var name from the two symbol tables.

    @Params:
    name: string, name of the variable.

    @Return:
    type_: string, variable type of variable.
    segment: string, segment the varaiable is located. One of the following:
    argument, local, this, static, or None if not found.
    index: integer, offset from segment base location in RAM. Or -1 if not
    found.
    """
    if subroutine_symbol_table.kind_of(name) != NONE:
        type_ = subroutine_symbol_table.type_of(name)
        kind = subroutine_symbol_table.kind_of(name)
        index = subroutine_symbol_table.index_of(name)
    elif class_symbol_table.kind_of(name) != NONE:
        type_ = class_symbol_table.type_of(name)
        kind = class_symbol_table.kind_of(name)
        index = class_symbol_table.index_of(name)
    else:
        return None, None, -1
    if kind == FIELD:
        kind = THIS
    return type_, kind, index


def generate_unique_marker():
    """
    Generate a unique marker.

    @Return:
    marker: a string which is unique in current class scope.
    """
    global unique_marker
    marker = unique_marker
    unique_marker += 1
    return str(marker)


def generate_label(tag):
    """
    Generate a label.

    @Params:
    tag: string, additional info to be added in the label.

    @Return
    label: string.
    """
    return class_name + "." + subroutine_name + "$" + tag

    
############## MAIN FUNCTION ############

def parse_single_file(input_filename, elem_list_from_tokenizer):
    """Parse single .jack file to .vm file."""

    vm_filename = input_filename[:input_filename.rfind('.jack')] + '.vm'
    global code_writer
    code_writer = VMWriter(vm_filename)

    global elem_list
    elem_list = list(elem_list_from_tokenizer)  # make a copy; not a reference
    global index
    index = 0

    compile_class()
    code_writer.close()
