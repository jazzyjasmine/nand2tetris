import sys
import re
import string


def parse_input_text(input_filename: str) -> None:
    """Delete whitespaces and comments of an input file.

    Args:
        input_filename: The absolute or relative path of
            the input file.

    """
    with open(input_filename, 'r') as file:
        lines = file.read()

    # delete comments starting with /* and ending with */ (in one line)
    temp_result = re.sub("/\*.*?\*/", "", lines)
    # delete comments starting with /* and ending with */ (span multiple lines)
    temp_result = re.sub("/\*([\s\S]*?)\*/", "\n", temp_result)
    # delete comments starting with // and ending with line return
    temp_result = re.sub("//.*?\n", "\n", temp_result + '\n')

    # get the output filename
    output_filename = input_filename[:input_filename.rfind(".in")] + ".out"

    # write to the output file
    with open(output_filename, 'w') as file:
        for line in temp_result.split("\n"):
            # delete whitespaces of each line
            for elem in string.whitespace:
                line = line.replace(elem, '')

            # if the line is empty after removing whitespaces, skip it
            if not line:
                continue

            file.write(line + '\n')


if __name__ == '__main__':
    parse_input_text(sys.argv[1])
