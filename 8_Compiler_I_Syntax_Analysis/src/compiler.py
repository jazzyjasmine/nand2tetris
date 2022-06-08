import os
import sys

from tokenizer import tokenize_single_file, INPUT_FILE_EXTENSION
from parser import parse_single_file


def main(directory_path):
    for content in os.listdir(directory_path):
        if not content.endswith(INPUT_FILE_EXTENSION):
            continue

        input_filename = os.path.join(directory_path, content)
        elem_list = tokenize_single_file(input_filename)
        parse_single_file(input_filename, elem_list)


if __name__ == '__main__':
    main(os.path.abspath(os.path.normpath(sys.argv[1])))
