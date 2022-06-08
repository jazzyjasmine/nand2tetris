from typing import List

PUSH_COMMAND_SUFFIX = [
    '@SP',
    'A=M',
    'M=D',
    '@SP',
    'M=M+1'
]

ADD_SUB_AND_OR_COMMAND_PREFIX = [
    '@SP',
    'AM=M-1',
    'D=M',
    'A=A-1'
]

NOT_NEG_COMMAND_PREFIX = [
    '@SP',
    'A=M-1'
]

INFINITE_LOOP = [
    '// infinite loop (not vm code)',
    '(INFINITE_LOOP)',
    '@INFINITE_LOOP',
    '0;JMP'
]

FUNCTION_DEF_CREATE_LOCAL_VAR = [
    '@SP',
    'AM=M+1',
    'A=A-1',
    'M=0'
]

continue_tag = 0
return_address_tag = 0


def translate_push_command(segment: str, index: str, class_name: str) -> List[str]:
    """Translate push command into assembly code"""
    if segment == 'local':
        return push_command_template('LCL', index, True)

    elif segment == 'argument':
        return push_command_template('ARG', index, True)

    elif segment == 'this':
        return push_command_template('THIS', index, True)

    elif segment == 'that':
        return push_command_template('THAT', index, True)

    elif segment == 'static':
        return push_command_template(f'{class_name}.{index}', index, False)  # static variable is globally unique in asm

    elif segment == 'temp':
        return push_command_template(str(int(index) + 5), index, False)

    elif segment == 'pointer' and index == '0':
        return push_command_template('THIS', index, False)

    elif segment == 'pointer' and index == '1':
        return push_command_template('THAT', index, False)

    else:
        # segment == 'constant'
        return [f'@{index}',
                'D=A',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1']


def translate_pop_command(segment: str, index: str, class_name: str) -> List[str]:
    if segment == 'local':
        return pop_command_template('LCL', index, True)

    elif segment == 'argument':
        return pop_command_template('ARG', index, True)

    elif segment == 'this':
        return pop_command_template('THIS', index, True)

    elif segment == 'that':
        return pop_command_template('THAT', index, True)

    elif segment == 'static':
        return pop_command_template(f'{class_name}.{index}', index, False)   # static variable is globally unique in asm

    elif segment == 'temp':
        return pop_command_template(str(int(index) + 5), index, False)

    elif segment == 'pointer' and index == '0':
        return pop_command_template('THIS', index, False)

    else:
        # segment == 'pointer' and index == '1'
        # no "pop constant ..." command
        return pop_command_template('THAT', index, False)


def push_command_template(segment: str, index: str, is_symbol: bool) -> List[str]:
    """Template for push command"""
    if is_symbol:
        return [f'@{segment}',
                'D=M',
                f'@{index}',
                'A=D+A',
                'D=M'] + PUSH_COMMAND_SUFFIX
    return [f'@{segment}', 'D=M'] + PUSH_COMMAND_SUFFIX


def pop_command_template(segment: str, index: str, is_symbol: bool) -> List[str]:
    """Template for pop command"""
    if is_symbol:
        return [f'@{segment}',
                'D=M',
                f'@{index}',
                'D=D+A',
                '@R13',
                'M=D',
                '@SP',
                'AM=M-1',
                'D=M',
                '@R13',
                'A=M',
                'M=D']
    return ['@SP',
            'AM=M-1',
            'D=M',
            f'@{segment}',
            'M=D']


def translate_arithmetic_or_boolean_command(operation: str) -> List[str]:
    """Translate arithmetic or boolean vm command into assembly code"""
    global continue_tag
    if operation == 'add':
        return ADD_SUB_AND_OR_COMMAND_PREFIX + ['M=D+M']
    elif operation == 'sub':
        return ADD_SUB_AND_OR_COMMAND_PREFIX + ['M=M-D']
    elif operation == 'and':
        return ADD_SUB_AND_OR_COMMAND_PREFIX + ['M=D&M']
    elif operation == 'or':
        return ADD_SUB_AND_OR_COMMAND_PREFIX + ['M=D|M']
    elif operation == 'gt':
        continue_tag += 1
        return gt_lt_eq_command_template('JGT', continue_tag)
    elif operation == 'lt':
        continue_tag += 1
        return gt_lt_eq_command_template('JLT', continue_tag)
    elif operation == 'eq':
        continue_tag += 1
        return gt_lt_eq_command_template('JEQ', continue_tag)
    elif operation == 'not':
        return NOT_NEG_COMMAND_PREFIX + ['M=!M']
    else:
        # operation == 'not'
        return NOT_NEG_COMMAND_PREFIX + ['M=-M']


def gt_lt_eq_command_template(jump_type: str, continue_tag: int) -> List[str]:
    """Template for gt, lt, eq command"""
    return ['@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'D=M-D',
            'M=-1',
            f'@CONTINUE{str(continue_tag)}',
            f'D;{jump_type}',
            '@SP',
            'A=M-1',
            'M=0',
            f'(CONTINUE{str(continue_tag)})']


def get_unique_label(label_name: str, curr_function_name: str) -> str:
    """Get globally unique label"""
    if not curr_function_name:
        return label_name
    else:
        return f'{curr_function_name}${label_name}'


def translate_label_command(label_name: str, curr_function_name: str) -> List[str]:
    """Translate label command into assembly code"""
    label = get_unique_label(label_name, curr_function_name)
    return [f'({label})']


def translate_goto_command(label_name: str, curr_function_name: str) -> List[str]:
    """Translate goto command into assembly code"""
    label = get_unique_label(label_name, curr_function_name)
    return [f'@{label}',
            '0;JMP']


def translate_if_goto_command(label_name: str, curr_function_name: str) -> List[str]:
    """Translate if-goto command into assembly code"""
    label = get_unique_label(label_name, curr_function_name)
    return ['@SP',
            'AM=M-1',
            'D=M',
            f'@{label}',
            'D;JNE']


def translate_function_call_command(function_name: str, argument_num: str) -> List[str]:
    """Translate function call command into assembly code"""
    global return_address_tag
    return_address_tag += 1
    return_address_segment = f'RETURN_ADDRESS{str(return_address_tag)}'
    return [   # push return address
               f'@{return_address_segment}',
               'D=A',
               '@SP',
               'A=M',
               'M=D',
               '@SP',
               'M=M+1'
           ] + \
           function_call_push_template('LCL') + \
           function_call_push_template('ARG') + \
           function_call_push_template('THIS') + \
           function_call_push_template('THAT') + \
           [  # ARG = SP - nArgs - 5
               '@SP',
               'D=M',
               f'@{int(argument_num) + 5}',
               'D=D-A',
               '@ARG',
               'M=D'
           ] + \
           [  # LCL = SP
               '@SP',
               'D=M',
               '@LCL',
               'M=D'
           ] + \
           [  # goto f, (return address)
               f'@{function_name}',
               "0;JMP",
               f'({return_address_segment})'
           ]


def function_call_push_template(segment: str) -> List[str]:
    """Template for push command in function call command"""
    return [
        f'@{segment}',
        'D=M',
        '@SP',
        'AM=M+1',
        'A=A-1',
        'M=D'
    ]


def translate_function_definition_command(function_name: str, local_var_num: str) -> List[str]:
    """Translate function definition command into assembly code"""
    return [f'({function_name})'] + FUNCTION_DEF_CREATE_LOCAL_VAR * int(local_var_num)


def translate_function_return_command() -> List[str]:
    """Translate function return command into assembly code"""
    return [
        '@LCL',  # FRAME = LCL
        'D=M',
        '@FRAME',
        'M=D',
        '@FRAME',  # RET = *(FRAME - 5)
        'D=M',
        '@5',
        'A=D-A',
        'D=M',
        '@RET',
        'M=D',
        '@SP',  # *ARG = pop()
        'AM=M-1',
        'D=M',
        '@ARG',
        'A=M',
        'M=D',
        '@ARG',  # SP = ARG + 1
        'D=M',
        '@SP',
        'M=D+1',
        '@FRAME',  # THAT = *(FRAME - 1)
        'A=M-1',
        'D=M',
        '@THAT',
        'M=D',
        '@FRAME',  # THIS = *(FRAME - 2)
        'D=M-1',
        'A=D-1',
        'D=M',
        '@THIS',
        'M=D',
        '@FRAME',  # ARG = *(FRAME - 3)
        'D=M-1',
        'D=D-1',
        'A=D-1',
        'D=M',
        '@ARG',
        'M=D',
        '@FRAME',  # LCL = *(FRAME - 4)
        'D=M',
        '@4',
        'A=D-A',
        'D=M',
        '@LCL',
        'M=D',
        '@RET',  # goto RET
        'A=M',
        '0;JMP'
    ]


def translate_bootstrap() -> List[str]:
    """Translate bootstrap command into assembly code"""
    return [
               '// bootstrap (not vm code)',
               '@256',
               'D=A',
               '@SP',
               'M=D'
           ] + translate_function_call_command('Sys.init', '0')
