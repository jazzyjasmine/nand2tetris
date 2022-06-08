import os

INPUT_FILE_EXTENSION = '.jack'
OUTPUT_FILE_EXTENSION = '.xml'
SPECIAL_SYMBOL_TO_TOKEN = {
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    '&': '&amp;'
}
index = 0


def compile_class(xml_writer, elem_list):
    xml_writer.write("<class>\n")
    write_keyword(xml_writer, "class")
    write_identifier(xml_writer, elem_list)
    write_symbol(xml_writer, "{")

    # classVarDec *
    while current_token(elem_list) in ["static", "field"]:
        compile_class_var_dec(xml_writer, elem_list)
    # subroutineDec *
    while current_token(elem_list) in ["constructor", "function", "method"]:
        compile_subroutine_dec(xml_writer, elem_list)

    write_symbol(xml_writer, "}")
    xml_writer.write("</class>\n")


def compile_class_var_dec(xml_writer, elem_list):
    xml_writer.write("<classVarDec>\n")
    write_keyword(xml_writer, current_token(elem_list))  # static | filed
    compile_type_without_tag(xml_writer, elem_list)  # type
    write_identifier(xml_writer, elem_list)  # varName
    while current_token(elem_list) == ",":
        write_symbol(xml_writer, ",")
        write_identifier(xml_writer, elem_list)
    write_symbol(xml_writer, ";")
    xml_writer.write("</classVarDec>\n")


def compile_subroutine_dec(xml_writer, elem_list):
    xml_writer.write("<subroutineDec>\n")
    write_keyword(xml_writer, current_token(elem_list))  # constructor | function | method
    compile_type_without_tag(xml_writer, elem_list)  # void | type
    write_identifier(xml_writer, elem_list)  # subroutineName
    write_symbol(xml_writer, "(")
    compile_parameter_list(xml_writer, elem_list)
    write_symbol(xml_writer, ")")
    compile_subroutine_body(xml_writer, elem_list)
    xml_writer.write("</subroutineDec>\n")


def compile_parameter_list(xml_writer, elem_list):
    xml_writer.write("<parameterList>\n")
    if current_token(elem_list) == ")":
        xml_writer.write("</parameterList>\n")
        return
    compile_type_without_tag(xml_writer, elem_list)  # type
    write_identifier(xml_writer, elem_list)  # varName
    while current_token(elem_list) == ",":
        write_symbol(xml_writer, ",")
        compile_type_without_tag(xml_writer, elem_list)
        write_identifier(xml_writer, elem_list)
    xml_writer.write("</parameterList>\n")


def compile_subroutine_body(xml_writer, elem_list):
    xml_writer.write("<subroutineBody>\n")
    write_symbol(xml_writer, "{")
    while current_token(elem_list) == "var":
        compile_var_dec(xml_writer, elem_list)
    compile_statements(xml_writer, elem_list)
    write_symbol(xml_writer, "}")
    xml_writer.write("</subroutineBody>\n")


def compile_var_dec(xml_writer, elem_list):
    xml_writer.write("<varDec>\n")
    write_keyword(xml_writer, "var")
    compile_type_without_tag(xml_writer, elem_list)
    write_identifier(xml_writer, elem_list)
    while current_token(elem_list) == ",":
        write_symbol(xml_writer, ",")
        write_identifier(xml_writer, elem_list)
    write_symbol(xml_writer, ";")
    xml_writer.write("</varDec>\n")


def compile_statements(xml_writer, elem_list):
    xml_writer.write("<statements>\n")
    while current_token(elem_list) in ["let", "if", "while", "do", "return"]:
        if current_token(elem_list) == "let":
            compile_let(xml_writer, elem_list)
        elif current_token(elem_list) == "if":
            compile_if(xml_writer, elem_list)
        elif current_token(elem_list) == "while":
            compile_while(xml_writer, elem_list)
        elif current_token(elem_list) == "do":
            compile_do(xml_writer, elem_list)
        else:
            compile_return(xml_writer, elem_list)
    xml_writer.write("</statements>\n")


def compile_let(xml_writer, elem_list):
    xml_writer.write("<letStatement>\n")
    write_keyword(xml_writer, "let")
    write_identifier(xml_writer, elem_list)  # varName
    if current_token(elem_list) == "[":
        write_symbol(xml_writer, "[")
        compile_expression(xml_writer, elem_list)
        write_symbol(xml_writer, "]")
    write_symbol(xml_writer, "=")
    compile_expression(xml_writer, elem_list)
    write_symbol(xml_writer, ";")
    xml_writer.write("</letStatement>\n")


def compile_if(xml_writer, elem_list):
    xml_writer.write("<ifStatement>\n")
    write_keyword(xml_writer, "if")
    write_symbol(xml_writer, "(")
    compile_expression(xml_writer, elem_list)
    write_symbol(xml_writer, ")")
    write_symbol(xml_writer, "{")
    compile_statements(xml_writer, elem_list)
    write_symbol(xml_writer, "}")
    if current_token(elem_list) == "else":
        write_keyword(xml_writer, "else")
        write_symbol(xml_writer, "{")
        compile_statements(xml_writer, elem_list)
        write_symbol(xml_writer, "}")
    xml_writer.write("</ifStatement>\n")


def compile_while(xml_writer, elem_list):
    xml_writer.write("<whileStatement>\n")
    write_keyword(xml_writer, "while")
    write_symbol(xml_writer, "(")
    compile_expression(xml_writer, elem_list)
    write_symbol(xml_writer, ")")
    write_symbol(xml_writer, "{")
    compile_statements(xml_writer, elem_list)
    write_symbol(xml_writer, "}")
    xml_writer.write("</whileStatement>\n")


def compile_do(xml_writer, elem_list):
    xml_writer.write("<doStatement>\n")
    write_keyword(xml_writer, "do")
    write_identifier(xml_writer, elem_list)
    if current_token(elem_list) == ".":
        write_symbol(xml_writer, ".")
        write_identifier(xml_writer, elem_list)
    write_symbol(xml_writer, "(")
    compile_expression_list(xml_writer, elem_list)
    write_symbol(xml_writer, ")")
    write_symbol(xml_writer, ";")
    xml_writer.write("</doStatement>\n")


def compile_return(xml_writer, elem_list):
    xml_writer.write("<returnStatement>\n")
    write_keyword(xml_writer, "return")
    if current_token(elem_list) != ";":
        compile_expression(xml_writer, elem_list)
    write_symbol(xml_writer, ";")
    xml_writer.write("</returnStatement>\n")


def compile_expression(xml_writer, elem_list):
    xml_writer.write("<expression>\n")
    compile_term(xml_writer, elem_list)
    while current_token(elem_list) in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
        write_symbol(xml_writer, current_token(elem_list))
        compile_term(xml_writer, elem_list)
    xml_writer.write("</expression>\n")


def compile_term(xml_writer, elem_list):
    xml_writer.write("<term>\n")
    if current_token(elem_list).isnumeric():
        write_integer(xml_writer, elem_list)
    elif current_token(elem_list).startswith("\""):
        write_string(xml_writer, elem_list)
    elif current_token(elem_list) in ["true", "false", "null", "this"]:
        write_keyword(xml_writer, current_token(elem_list))
    elif current_token(elem_list) == "(":
        write_symbol(xml_writer, "(")
        compile_expression(xml_writer, elem_list)
        write_symbol(xml_writer, ")")
    elif current_token(elem_list) in ["~", "-"]:
        write_symbol(xml_writer, current_token(elem_list))
        compile_term(xml_writer, elem_list)
    # varName | varName [ expression ] | subroutineCall
    else:
        write_identifier(xml_writer, elem_list)
        # [ expression ]
        if current_token(elem_list) == "[":
            write_symbol(xml_writer, "[")
            compile_expression(xml_writer, elem_list)
            write_symbol(xml_writer, "]")
        # subroutineCall
        elif current_token(elem_list) == "(" or current_token(elem_list) == ".":
            if current_token(elem_list) == ".":
                write_symbol(xml_writer, ".")
                write_identifier(xml_writer, elem_list)
            write_symbol(xml_writer, "(")
            compile_expression_list(xml_writer, elem_list)
            write_symbol(xml_writer, ")")
    xml_writer.write("</term>\n")


def compile_expression_list(xml_writer, elem_list):
    xml_writer.write("<expressionList>\n")
    if current_token(elem_list) == ")":
        xml_writer.write("</expressionList>\n")
        return
    compile_expression(xml_writer, elem_list)
    while current_token(elem_list) == ",":
        write_symbol(xml_writer, ",")
        compile_expression(xml_writer, elem_list)
    xml_writer.write("</expressionList>\n")


# Helper methods

def compile_type_without_tag(xml_writer, elem_list):
    if (current_token(elem_list) == "int" or current_token(elem_list) == "char"
            or current_token(elem_list) == "boolean" or current_token(elem_list) == "void"):
        write_keyword(xml_writer, current_token(elem_list))
    else:
        write_identifier(xml_writer, elem_list)


def current_token(elem_list):
    if index > len(elem_list):
        return ""
    return elem_list[index]


def write_keyword(xml_writer, word):
    xml_writer.write("<keyword> ")
    xml_writer.write(word)
    xml_writer.write(" </keyword>\n")
    global index
    index += 1


def write_symbol(xml_writer, symbol):
    xml_writer.write("<symbol> ")
    if symbol in SPECIAL_SYMBOL_TO_TOKEN:
        xml_writer.write(SPECIAL_SYMBOL_TO_TOKEN[symbol])
    else:
        xml_writer.write(symbol)
    xml_writer.write(" </symbol>\n")
    global index
    index += 1


def write_integer(xml_writer, elem_list):
    xml_writer.write("<integerConstant> ")
    xml_writer.write(current_token(elem_list))
    xml_writer.write(" </integerConstant>\n")
    global index
    index += 1


def write_string(xml_writer, elem_list):
    xml_writer.write("<stringConstant> ")
    xml_writer.write(current_token(elem_list)[1:-1])
    xml_writer.write(" </stringConstant>\n")
    global index
    index += 1


def write_identifier(xml_writer, elem_list):
    xml_writer.write("<identifier> ")
    xml_writer.write(current_token(elem_list))
    xml_writer.write(" </identifier>\n")
    global index
    index += 1


def parse_single_file(input_filename, elem_list):
    global index
    index = 0
    directory_path = os.path.dirname(input_filename)
    parser_directory = os.path.join(directory_path, 'ParserOutputs')
    if not os.path.exists(parser_directory):
        os.makedirs(parser_directory)

    input_file_basename = os.path.basename(input_filename)
    output_filename = input_file_basename[:input_file_basename.rfind(INPUT_FILE_EXTENSION)] + OUTPUT_FILE_EXTENSION

    xml_writer = open(os.path.join(parser_directory, output_filename), 'w')
    compile_class(xml_writer, elem_list)
    xml_writer.close()
