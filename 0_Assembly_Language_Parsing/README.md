# Assembly Language Parsing

## Functionality
### 1. Remove white space
Strip out all white space from ```<filename>```.in. White space in this case means spaces, tabs, and blank lines, but not line returns.
### 2. Remove comments
Remove all comments in addition to the whitespace. Comments come in two forms:
- comments begin with the sequence "//" and end at the line return
- comments begin with the sequence /* and end at the sequence */

## How to use
1. Run ```python3 parse.py <filename>``` in command line. The filename is an absolute or relative path of the input file, and it must end with ".in"
2. The output file ```<filename>```.out will be written to the directory where ```<filename>```.in resides