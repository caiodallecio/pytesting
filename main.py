import ast
import sys
import os.path
import pickle as pk
import hashlib as hs
import astunparse



class TreeData():
    def __init__(self, ast_tree):
        hasher = hs.sha512()
        nodes = get_all_nodes(ast_tree)
        hasher.update(bytes(ast.dump(ast_tree), 'utf-8'))
        self.hash = hasher.digest()
        self.function_declarations = get_all_functions(nodes)
        self.function_calls = get_all_functions_calls(nodes)
        self.tree = ast_tree

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def update_test_file(self,name):
        old_tree = TreeData(parse_ast(name))
        new_tree = TreeData(ast.parse(self.generate_test_file(name)))
        for nw_node in new_tree.function_declarations:
            for od_node in old_tree.function_declarations:
                if nw_node.name == od_node.name:
                    nw_node.body = od_node.body
        return astunparse.unparse(new_tree.tree)

    def generate_test_file(self, file_name):
        ret = []

        module_name = file_name.split('_')[1].split('.')[0]
        ret += generate_test_imports([
            (module_name, 'module'),
            ('unittest', 'test'),
            ('hypothesis','hyp')])
        ret.append('class Test%s(test.TestCase):\n\t' % module_name)

        for func in self.function_declarations:
            ret += generate_test_function(func)


        ret.append('if __name__ == \'__main__\':')
        ret.append('\ttest.main()')
        ret = '\n'.join(ret)
        return ret
            
            


def generate_test_imports(import_list):
        ret = []
        for imp in import_list:
            if isinstance(imp, tuple):
                ret.append('import %s as %s' % (imp[0], imp[1]))
            else:
                ret.append('import %s' % imp)
        return ret

    
def generate_test_function(func):
    ret = []
    ret.append('\tdef test_%s(self):' % func.name)
    ret.append('\t\tself.assertTrue(False)')
    ret.append('\n')
    return ret


def get_all_nodes(ast_tree):
    return [n for n in ast.walk(ast_tree)]

def write_test_file(file_name,data):
    with open(file_name, 'w') as handle:
        handle.write(data)

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
def foo():
    pass

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        tree = TreeData(parse_ast(filename))
        data_name = 'data_' + filename.split('.')[0] + '.pk'
        test_name = 'test_' + filename.split('.')[0] + '.py'
        if not os.path.isfile(data_name):
            serialize_tree_data(data_name, tree)
            tree.generate_test_file('test_' + filename.split('.')[0] + '.py')
        elif tree == un_serialize_tree_data(data_name):
            print('No changes')
        else:
            print('Changes Generating new Test File')
            
            if os.path.isfile(test_name):

                test_source = tree.update_test_file(test_name)
            else:
                test_source = tree.generate_test_file(test_name)

            serialize_tree_data(data_name, tree)
            write_test_file(test_name,test_source)




