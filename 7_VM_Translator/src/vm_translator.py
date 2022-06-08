import re
import sys
import os
from typing import List

import assembly_generator

INPUT_FILE_EXTENSION = '.vm'
OUTPUT_FILE_EXTENSION = '.asm'


def parse_input_file(input_filename: str) -> List[str]:
    """Remove comments and whitespaces for input file"""
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
        # if the line is empty after removing whitespaces, skip it
        if not line:
            continue

        parsed_input_list.append(line.strip())

    return parsed_input_list


def get_assembly_code_list(parsed_input_list: List[str], class_name: str) -> List[str]:
    """Get the assembly code list from parsed input list"""
    assembly_code_list = []
    curr_function_name = None

    for vm_line_string in parsed_input_list:
        # classify: memory access command or arithmetic/boolean command
        vm_line_list = vm_line_string.split()
        command_header = vm_line_list[0]
        assembly_code_list.extend([f'// {vm_line_string}'])
        # memory access command: push
        if command_header == 'push':
            assembly_code_list.extend(assembly_generator.translate_push_command(vm_line_list[1],
                                                                                vm_line_list[2],
                                                                                class_name))
        # memory access command: pop
        elif command_header == 'pop':
            assembly_code_list.extend(assembly_generator.translate_pop_command(vm_line_list[1],
                                                                               vm_line_list[2],
                                                                               class_name))

        # program flow command: label
        elif command_header == 'label':
            assembly_code_list.extend(assembly_generator.translate_label_command(vm_line_list[1],
                                                                                 curr_function_name))

        # program flow command: goto
        elif command_header == 'goto':
            assembly_code_list.extend(assembly_generator.translate_goto_command(vm_line_list[1],
                                                                                curr_function_name))

        # program flow command: if-goto
        elif command_header == 'if-goto':
            assembly_code_list.extend(assembly_generator.translate_if_goto_command(vm_line_list[1],
                                                                                   curr_function_name))

        # function call command
        elif command_header == 'call':
            assembly_code_list.extend(assembly_generator.translate_function_call_command(vm_line_list[1],
                                                                                         vm_line_list[2]))

        # function definition command
        elif command_header == 'function':
            curr_function_name = vm_line_list[1]
            assembly_code_list.extend(assembly_generator.translate_function_definition_command(vm_line_list[1],
                                                                                               vm_line_list[2]))

        # function return command
        elif command_header == 'return':
            assembly_code_list.extend(assembly_generator.translate_function_return_command())

        # arithmetic/boolean command
        else:
            assembly_code_list.extend(assembly_generator.translate_arithmetic_or_boolean_command(vm_line_list[0]))

    return assembly_code_list


def write_to_asm_file(directory_path: str, assembly_code_list: List[str]) -> None:
    """Write assembly code to .asm file"""
    output_filename = os.path.basename(directory_path) + OUTPUT_FILE_EXTENSION
    with open(os.path.join(directory_path, output_filename), 'w') as file:
        for assembly_code_string in assembly_code_list:
            file.write(assembly_code_string + '\n')


def translate_vm_to_assembly(directory_path: str) -> None:
    """Translate vm code to assembly code"""
    assembly_code_list = []
    vm_file_count = 0
    for content in os.listdir(directory_path):
        if not content.endswith(INPUT_FILE_EXTENSION):
            continue

        vm_file_count += 1
        input_filename = os.path.join(directory_path, content)
        class_name = content[:content.rfind(INPUT_FILE_EXTENSION)]  # class name is the vm file name without extension
        assembly_code_list.extend(get_assembly_code_list(parse_input_file(input_filename), class_name))

    # if more than one vm file in directory, add bootstrap at the beginning of the asm code
    if vm_file_count > 1:
        assembly_code_list = assembly_generator.translate_bootstrap() + assembly_code_list

    # add infinite loop at the end of the asm code
    assembly_code_list.extend(assembly_generator.INFINITE_LOOP)

    write_to_asm_file(directory_path, assembly_code_list)


if __name__ == '__main__':
    translate_vm_to_assembly(os.path.normpath(sys.argv[1]))  # python3 vm_translator.py <directory_path>
