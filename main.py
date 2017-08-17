import ast
import sys
import os.path
import pickle as pk


def get_all_functions(ast_tree):
    return [n for n in ast.walk(ast_tree) if isinstance(n, ast.FunctionDef)]


def get_all_functions_calls(ast_tree):
    return [n for n in ast.walk(ast_tree) if isinstance(n, ast.Call)]


def parse_ast(file_name):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=file_name)


def create_serial_object(ast_tree):
    function_def = get_all_functions(ast_tree)
    function_calls = get_all_functions_calls(ast_tree)
    return [function_def, function_calls]


def serialize_tree_data(file_name, ast_tree):
    with open(file_name, 'wb') as file:
        pk.dump(create_serial_object(ast_tree), file)


def un_serialize_tree_data(file_name):
    with open(file_name, 'rb') as file:
        return pk.load(file)


def compare_ast(ast1, ast2):
    return ast.dump(ast1) == ast.dump(ast2)


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        tree = parse_ast(filename)
        data_name = 'data_' + filename.split('.')[0] + '.pk'
        if not os.path.isfile(data_name):
            serialize_tree_data(data_name, tree)
        elif map(ast.dump,un_serialize_tree_data(data_name))[:] == map(ast.dump,create_serial_object(tree))[:]:
            print('No changes')
        else:
            print(list(map(ast.dump,create_serial_object(tree))))



