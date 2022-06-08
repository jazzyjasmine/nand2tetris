import sys
import re
import string
from typing import List


SYMBOL_TABLE = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN': 16384,
    'KBD': 24576
}

# commutative operations are handled, e.g. D+A and A+D
MD_COMP_TABLE = {
    'M': '110000',
    '!M': '110001',
    '-M': '110011',
    'M+1': '110111',
    '1+M': '110111',
    'M-1': '110010',
    'D+M': '000010',
    'M+D': '000010',
    'D-M': '010011',
    'M-D': '000111',
    'D&M': '000000',
    'M&D': '000000',
    'D|M': '010101',
    'M|D': '010101'
}

AD_COMP_TABLE = {
    '0': '101010',
    '1': '111111',
    '-1': '111010',
    'D': '001100',
    'A': '110000',
    '!D': '001101',
    '!A': '110001',
    '-D': '001111',
    '-A': '110011',
    'D+1': '011111',
    '1+D': '011111',
    'A+1': '110111',
    '1+A': '110111',
    'D-1': '001110',
    'A-1': '110010',
    'D+A': '000010',
    'A+D': '000010',
    'D-A': '010011',
    'A-D': '000111',
    'D&A': '000000',
    'A&D': '000000',
    'D|A': '010101',
    'A|D': '010101'
}

DEST_TABLE = {
    'null': '000',
    'M': '001',
    'D': '010',
    'DM': '011',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'MA': '101',
    'AD': '110',
    'DA': '110',
    'ADM': '111',
    'AMD': '111',
    'MAD': '111',
    'MDA': '111',
    'DAM': '111',
    'DMA': '111'
}

JUMP_TABLE = {
    'null': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

START_POSITION = 16  # start ram position for self-defined variable in A-instruction
INPUT_FILE_EXTENSION = '.asm'  # extension of input file
OUTPUT_FILE_EXTENSION = '.hack'  # extension of output file


def parse_input_file(input_filename: str) -> List[str]:
    """Remove comments and whitespaces for input file

    Args:
        input_filename: Absolute or relative path of the
            input file

    Returns:
        A list of strings, where each string represents
            one line of assembly command after removing
            comments and whitespaces.

    """
    with open(input_filename, 'r') as file:
        lines = file.read()

    # delete comments starting with /* and ending with */ (in one line)
    temp_result = re.sub("/\*.*?\*/", "", lines)
    # delete comments starting with /* and ending with */ (span multiple lines)
    temp_result = re.sub("/\*([\s\S]*?)\*/", "\n", temp_result)
    # delete comments starting with // and ending with line return
    temp_result = re.sub("//.*?\n", "\n", temp_result + '\n')

    parsed_input_list = []

    for line in temp_result.split("\n"):
        # delete whitespaces of each line
        for elem in string.whitespace:
            line = line.replace(elem, '')

        # if the line is empty after removing whitespaces, skip it
        if not line:
            continue

        parsed_input_list.append(line)

    return parsed_input_list


def process_parentheses(parsed_input_list: List[str]) -> None:
    """Detect and process assembly command with parentheses

    Args:
        parsed_input_list: A list of assembly command after
            removing comments and whitespaces

    """
    line_number = -1
    detected_parentheses_count = 0  # number of lines with parentheses that have been detected
    for line in parsed_input_list:
        line_number += 1
        # if the line is in format "(***)"
        if line[0] == '(':
            # get the variable name inside the parentheses
            curr_symbol = line[1:-1]
            # update symbol table by inserting the variable name and corresponding line number
            SYMBOL_TABLE[curr_symbol] = line_number - detected_parentheses_count
            detected_parentheses_count += 1


def encode_machine_language(parsed_input_list: List[str]) -> List[str]:
    """Translate assembly language into machine language

    Args:
        parsed_input_list: A list of assembly command after
            removing comments and whitespaces

    Returns:
        A list of machine code translated from the input
            assembly codes

    """
    machine_language_list = []
    a_instruction_symbol_count = 0  # number of self-defined variable in A-instruction

    for line in parsed_input_list:
        # if (***), skip it
        if line[0] == '(':
            continue

        # each line is either an A-instruction or C-instruction
        # if A-instruction
        if line[0] == '@':
            # get the symbol after @
            curr_symbol = line[1:]
            # if no symbol in A-instruction, e.g. @12
            if curr_symbol.isnumeric():
                # directly translate the number into 16-bit binary code
                machine_language_list.append(format(int(curr_symbol), '016b'))
            # if self-defined symbol in A-instruction, e.g. @counter
            else:
                # if the self-defined symbol is a new one (not in symbol table)
                if curr_symbol not in SYMBOL_TABLE:
                    # compute the ram location assigned to the self-defined variable
                    assigned_ram_location = START_POSITION + a_instruction_symbol_count
                    # insert the new symbol with its ram location into symbol table
                    SYMBOL_TABLE[curr_symbol] = assigned_ram_location
                    # increase the number of self-defined variable in A-instruction by 1
                    a_instruction_symbol_count += 1
                # translate into machine language by ram location
                machine_language_list.append(format(SYMBOL_TABLE[curr_symbol], '016b'))
            continue

        # if C-instruction
        # 1) compute the jump code
        # if there is a jump instruction, e.g. 0;JMP
        if ';' in line:
            jump_instruction = line.split(";")[1]
            jump_code = JUMP_TABLE[jump_instruction]
            non_jump_instruction = line.split(";")[0]
        else:
            jump_code = JUMP_TABLE['null']
            non_jump_instruction = line

        # 2) compute the dest code
        # if no destination, i.e. no "=" sign
        if '=' not in non_jump_instruction:
            dest_code = DEST_TABLE['null']
            comp_instruction = non_jump_instruction
        else:
            # dest instruction is in the left-hand side of "="
            dest_code = DEST_TABLE[non_jump_instruction.split("=")[0]]
            comp_instruction = non_jump_instruction.split("=")[1]

        # 3) compute the comp code
        if 'M' in comp_instruction:
            a_code = '1'
            comp_code = MD_COMP_TABLE[comp_instruction]  # the comp_code does not include a_code
        else:
            a_code = '0'
            comp_code = AD_COMP_TABLE[comp_instruction]

        # merge the codes into one line
        machine_language_list.append('111' + a_code + comp_code + dest_code + jump_code)

    return machine_language_list


def write_to_hack_file(input_filename: str, machine_language_list: List[str]) -> None:
    """Write the machine codes into .hack file

    Args:
        input_filename: Absolute or relative path of the
            input file
        machine_language_list: A list of machine code translated
            from the input file

    """
    output_filename = input_filename[:input_filename.rfind(INPUT_FILE_EXTENSION)] + OUTPUT_FILE_EXTENSION
    with open(output_filename, 'w') as file:
        for line in machine_language_list:
            file.write(line + '\n')


def assemble(input_filename: str) -> None:
    """Assemble the input file

    Args:
        input_filename: Absolute or relative path of the
            input file

    """
    parsed_input_list = parse_input_file(input_filename)
    process_parentheses(parsed_input_list)
    write_to_hack_file(input_filename, encode_machine_language(parsed_input_list))


if __name__ == "__main__":
    assemble(sys.argv[1])
