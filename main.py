import ast
import sys
import os.path
import pickle as pk
import hashlib as hs


def get_all_nodes(ast_tree):
    return [n for n in ast.walk(ast_tree)]


def get_all_functions(nodes):
    return [n for n in nodes if isinstance(n, ast.FunctionDef)]


def get_all_functions_calls(nodes):
    return [n for n in nodes if isinstance(n, ast.Call)]


def parse_ast(file_name):
    with open(file_name, "rt") as handle:
        return ast.parse(handle.read(), filename=file_name)


def create_serial_object(ast_tree):
    obj = []
    hasher = hs.sha512()
    nodes = get_all_nodes(ast_tree)
    hasher.update(bytes(ast.dump(ast_tree), 'utf-8'))
    ident = hasher.digest()
    obj.append(ident)
    obj.append(get_all_functions(nodes))
    obj.append(get_all_functions_calls(nodes))
    return obj


def serialize_tree_data(file_name, ast_tree):
    with open(file_name, 'wb') as handle:
        pk.dump(create_serial_object(ast_tree), handle)


def un_serialize_tree_data(file_name):
    with open(file_name, 'rb') as handle:
        return pk.load(handle)


def compare_tree_data_objects(a,b):
    if a[0] == b[0]:
        return True
    return False  


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        tree = parse_ast(filename)
        data_name = 'data_' + filename.split('.')[0] + '.pk'
        if not os.path.isfile(data_name):
            serialize_tree_data(data_name, tree)
        elif compare_tree_data_objects(create_serial_object(tree), un_serialize_tree_data(data_name)):
            print('No changes')
        else:
            print('Changes')



