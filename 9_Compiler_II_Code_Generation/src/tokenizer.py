import re
import os
from constants import *


def parse_input_file(input_filename: str):
    """Remove comments and whitespaces for input file"""
    with open(input_filename, 'r') as file:
        lines = file.read()

    # delete comments starting with /* and ending with */ (in one line)
    temp_result = re.sub("/\*.*?\*/", "", lines)
    # delete comments starting with /* and ending with */ (span multiple lines)
    temp_result = re.sub("/\*([\s\S]*?)\*/", "\n", temp_result)
    # delete comments starting with // and ending with line return
    temp_result = re.sub("//.*?\n", "\n", temp_result + '\n')

    parsed_input_string = ''

    for line in temp_result.split("\n"):
        # if the line is empty after removing whitespaces, skip it
        if not line:
            continue

        parsed_input_string += line.strip() + ' '

    return parsed_input_string[:-1]


def replace_strings_with_signs(parsed_input_string):
    sign_to_string = {}
    string_count = 0
    len_diff = 0
    for match in re.finditer(r'"(.*?)"', parsed_input_string):
        cur_sign = f'@{string_count}@'
        string_count += 1
        sign_to_string[cur_sign] = match.group()
        parsed_input_string = parsed_input_string[:match.span()[0] - len_diff] + \
                              cur_sign + \
                              parsed_input_string[match.span()[1] - len_diff:]
        len_diff += len(match.group()) - len(cur_sign)
    return sign_to_string, parsed_input_string


def add_whitespaces_for_symbols(parsed_input_string):
    for symbol in SYMBOLS:
        parsed_input_string = parsed_input_string.replace(symbol, f' {symbol} ')
    return parsed_input_string


def get_token_list(sign_to_string, parsed_input_string):
    token_list = ['<tokens>']
    elem_list = parsed_input_string.split()
    for elem in elem_list:
        if elem in SYMBOLS:
            token = elem
            if elem in SPECIAL_SYMBOL_TO_TOKEN:
                token = SPECIAL_SYMBOL_TO_TOKEN[elem]
            token_list.append(f'<symbol> {token} </symbol>')
        elif elem in sign_to_string:
            token_list.append(f'<stringConstant> {sign_to_string[elem][1:-1]} </stringConstant>')
        elif elem in KEYWORDS:
            token_list.append(f'<keyword> {elem} </keyword>')
        elif elem.isnumeric():
            token_list.append(f'<integerConstant> {elem} </integerConstant>')
        else:
            token_list.append(f'<identifier> {elem} </identifier>')
    token_list.append('</tokens>')
    return token_list, elem_list


def write_token_list_to_file(input_filename, token_list):
    directory_path = os.path.dirname(input_filename)
    token_directory = os.path.join(directory_path, 'TokenizerOutputs')
    if not os.path.exists(token_directory):
        os.makedirs(token_directory)

    input_file_basename = os.path.basename(input_filename)
    output_filename = input_file_basename[:input_file_basename.rfind(INPUT_FILE_EXTENSION)] + OUTPUT_FILE_SUFFIX

    with open(os.path.join(token_directory, output_filename), 'w') as writer:
        for token_line in token_list:
            writer.write(token_line + '\n')


def get_elem_list_for_parser(sign_to_string, elem_list):
    for index, elem in enumerate(elem_list):
        if elem in sign_to_string:
            elem_list[index] = sign_to_string[elem]
    return elem_list


def tokenize_single_file(input_filename):
    parsed_input_string = parse_input_file(input_filename)
    sign_to_string, parsed_input_string = replace_strings_with_signs(parsed_input_string)
    parsed_input_string = add_whitespaces_for_symbols(parsed_input_string)
    token_list, elem_list = get_token_list(sign_to_string, parsed_input_string)
    # write_token_list_to_file(input_filename, token_list)
    return get_elem_list_for_parser(sign_to_string, elem_list)
