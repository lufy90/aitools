
import clang.cindex
clang.cindex.Config.set_library_path('/usr/lib/llvm-7/lib/')

def extract_functions_from_ast(node):
    """
    Recursively traverse the AST and find all function definitions.
    """
    functions = []
    if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        func_name = node.spelling
        return_type = node.result_type.spelling
        params = [param.spelling for param in node.get_arguments()]
        functions.append((return_type, func_name, params))

    for child in node.get_children():
        functions.extend(extract_functions_from_ast(child))

    return functions

def write_function_files(functions, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for return_type, func_name, params in functions:
        # Create a new C file for each function
        func_file_path = os.path.join(output_dir, f'{func_name}.c')

        with open(func_file_path, 'w') as f:
            # Write the function definition in the format
            f.write(f"{return_type} {func_name}({', '.join([str(arg) for arg in params])}) {{\n")
            f.write(f"    // Function body (not extracted here)\n")
            f.write("}\n")

        print(f"Function '{func_name}' written to {func_file_path}")

def main(input_file):
    #input_file = 'example.c'  # Path to the input C file
    output_dir = 'output'     # Output directory where functions will be saved

    # Load the C file using clang
    index = clang.cindex.Index.create()
    translation_unit = index.parse(input_file)

    # Extract functions from the AST
    functions = extract_functions_from_ast(translation_unit.cursor)

    # Write the functions into separate files
    write_function_files(functions, output_dir)

    print(f"Functions have been written to '{output_dir}'.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
