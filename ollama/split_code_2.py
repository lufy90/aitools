
import os
from pycparser import c_parser, c_ast

def extract_functions_from_c(code):
    parser = c_parser.CParser()
    ast = parser.parse(code)  # Parse the C code into an AST (Abstract Syntax Tree)

    functions = []

    # Traverse the AST to find all function definitions
    for node in ast.ext:
        if isinstance(node, c_ast.FuncDef):
            # Function name
            func_name = node.decl.name

            # Function return type and parameters
            return_type = node.decl.type
            params = node.decl.type.args

            # Function body (we extract it as well)
            body = node.body

            # Store function data (return type, name, params, body)
            functions.append((return_type, func_name, params, body))

    return functions

def write_function_files(functions, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for return_type, func_name, params, body in functions:
        # Create a new C file for each function
        func_file_path = os.path.join(output_dir, f'{func_name}.c')

        with open(func_file_path, 'w') as f:
            # Write the function definition in the format
            f.write(f"{return_type} {func_name}({', '.join([str(arg) for arg in params])}) {{\n")
            f.write(f"    {body}\n")
            f.write("}\n")

        print(f"Function '{func_name}' written to {func_file_path}")

def write_header_file(functions, header_file):
    with open(header_file, 'w') as f:
        f.write("#ifndef FUNCTIONS_H\n")
        f.write("#define FUNCTIONS_H\n\n")

        # Write the function prototypes (declarations)
        for return_type, func_name, params, _ in functions:
            f.write(f"{return_type} {func_name}({', '.join([str(arg) for arg in params])});\n")

        f.write("\n#endif\n")

def main(input_file):
    #input_file = 'example.c'  # Path to the input C file
    output_dir = 'output'     # Output directory where functions will be saved
    header_file = os.path.join(output_dir, 'functions.h')  # Header file with function prototypes

    # Read the C code from the input file
    with open(input_file, 'r') as f:
        c_code = f.read()

    # Extract functions from the C code
    functions = extract_functions_from_c(c_code)

    # Write the functions into separate files
    write_function_files(functions, output_dir)

    # Write the header file
    write_header_file(functions, header_file)

    print(f"Header file and function files have been written to '{output_dir}'.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
