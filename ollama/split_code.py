
import re
import os

# Function to extract all functions from C code
def extract_functions(c_code):
    # Regular expression to match C function definitions
    func_pattern = r'(\w[\w\d_]*\s+[\w\d_]+)\s*\((.*?)\)\s*\{(.*?)\}'  # captures return type, name, params, and body
    func_pattern = r'''
        ^\s*                              # Skip leading whitespaces
        (                                # Start of function return type group
            [\w\s\*\(\)\[\],]+           # Capture the return type (includes pointers, arrays)
        )\s+                             # Return type followed by spaces
        (\w[\w\d_]+)                     # Function name (identifier)
        \s*\(                            # Opening parenthesis for function parameters
        ([^)]*)                          # Capture function parameters (everything inside the parentheses)
        \)\s*                            # Closing parenthesis and optional whitespace
        \{                               # Opening curly brace of function body
        ([^{}]*)                         # Function body (non-nested content)
        \}                               # Closing curly brace of function body
    '''

    # Find all function matches
    functions = re.findall(func_pattern, c_code, re.VERBOSE | re.DOTALL)

    return functions

# Function to write function declaration in header
def write_header(functions, header_file):
    with open(header_file, 'w') as f:
        f.write('#ifndef FUNCTIONS_H\n')
        f.write('#define FUNCTIONS_H\n\n')

        for return_type, func_name, params, _ in functions:
            # Write function declaration (prototype)
            f.write(f"{return_type} {func_name}({params});\n")

        f.write('\n#endif\n')

# Function to write individual functions into separate C files
def write_function_files(functions, source_dir):
    for return_type, func_name, params, body in functions:
        func_file = os.path.join(source_dir, f'{func_name}.c')

        # Write the function definition to a file
        with open(func_file, 'w') as f:
            f.write(f"{return_type} {func_name}({params}) {{\n")
            f.write(body.strip() + '\n')
            f.write('}\n')

# Function to write the main file
def write_main_file(main_file, header_file, function_names):
    with open(main_file, 'w') as f:
        f.write('#include "' + header_file + '"\n\n')

        f.write('int main() {\n')
        for func_name in function_names:
            f.write(f"    {func_name}();\n")  # You can call each function here
        f.write('    return 0;\n')
        f.write('}\n')

# Main logic to split the C code
def split_c_code(c_file, output_dir):
    # Read the source C file
    with open(c_file, 'r') as f:
        c_code = f.read()

    # Extract functions using regex
    functions = extract_functions(c_code)

    for i in functions:
        print("================================================")
        print(i)

    # Extract function names for main file and for header
    function_names = [func_name for _, func_name, _, _ in functions]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write header file
    header_file = os.path.join(output_dir, 'functions.h')
    write_header(functions, header_file)

    # Write individual function C files
    write_function_files(functions, output_dir)

    # Write the main file
    main_file = os.path.join(output_dir, 'main.c')
    write_main_file(main_file, 'functions.h', function_names)

    print(f"Splitting C code complete. Files are saved in: {output_dir}")

# Example usage
import sys
split_c_code(sys.argv[1], 'output')

