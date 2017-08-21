import ast
import sys
import os.path
import pickle as pk
import hashlib as hs


class TreeData:
    def __init__(self, ast_tree):
        hasher = hs.sha512()
        nodes = get_all_nodes(ast_tree)
        hasher.update(bytes(ast.dump(ast_tree), 'utf-8'))
        self.hash = hasher.digest()
        self.function_declarations = get_all_functions(nodes)
        self.function_calls = get_all_functions_calls(nodes)

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not self.__eq__(other)

    def generate_test_file(self, file_name):
        with open(file_name, 'w') as handle:
            module_name = file_name.split('_')[1].split('.')[0]
            handle.writelines([
                'import %s as module\n' % module_name,
                'import %s\n' % 'unittest',
                'class Test%s(unittest.TestCase):\n\t' % module_name])


def get_all_nodes(ast_tree):
    return [n for n in ast.walk(ast_tree)]


def get_all_functions(nodes):
    return [n for n in nodes if isinstance(n, ast.FunctionDef)]


def get_all_functions_calls(nodes):
    return [n for n in nodes if isinstance(n, ast.Call)]


def parse_ast(file_name):
    with open(file_name, "rt") as handle:
        return ast.parse(handle.read(), filename=file_name)


def serialize_tree_data(file_name, tree_data):
    with open(file_name, 'wb') as handle:
        pk.dump(tree_data, handle)


def un_serialize_tree_data(file_name):
    with open(file_name, 'rb') as handle:
        return pk.load(handle)


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        tree = TreeData(parse_ast(filename))
        data_name = 'data_' + filename.split('.')[0] + '.pk'
        if not os.path.isfile(data_name):
            serialize_tree_data(data_name, tree)
            tree.generate_test_file('test_' + filename.split('.')[0] + '.py')
        elif tree == un_serialize_tree_data(data_name):
            print('No changes')
        else:
            print('Changes Generating new Test File')
            tree.generate_test_file('test_' + filename.split('.')[0] + '.py')




