import ast
import sys
import os.path
import pickle as pk
import hashlib as hs
import astunparse
import typing as tp




class TreeData():
    def __init__(self, ast_tree):
        hasher = hs.sha512()
        hasher.update(bytes(ast.dump(ast_tree), 'utf-8'))
        self.hash = hasher.digest()
        self.tree = ast_tree

    def __eq__(self, other):
        return self.hash == other.hash


    def __ne__(self, other):
        return not self.__eq__(other)
    

    def get_all_nodes(self):
        return [n for n in ast.walk(self.tree)]
    

    def get_all_functions_declarations(self):
        return [n for n in self.get_all_nodes() if isinstance(n, ast.FunctionDef)]

    def get_all_functions_calls(self):
        return [n for n in self.get_all_nodes() if isinstance(n, ast.Call)]
    def get_all_static_function_declarations(self):
        all_foos = self.get_all_functions_declarations()
        return [n for n in all_foos if len(n.args.args) == 0 or not n.args.args[0].arg == 'self' ]

    def update_test_file(self,name):
        old_tree = TreeData(parse_ast(name))
        new_tree = TreeData(ast.parse(self.generate_test_file(name)))
        for nw_node in new_tree.get_all_functions_declarations():
            for od_node in old_tree.get_all_functions_declarations():
                if nw_node.name == od_node.name:
                    nw_node.body = od_node.body
        return astunparse.unparse(new_tree.tree)

    def generate_test_file(self, file_name):
        ret = []

        module_name = file_name.split('_')[1].split('.')[0]
        ret += generate_test_imports([
            (module_name, 'module'),
            ('unittest', 'test'),
            ('hypothesis','hyp'),
            ('hypothesis.strategies', 'st')])
        ret.append('class Test%s(test.TestCase):\n\t' % module_name)

        for func in self.get_all_static_function_declarations():
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



def get_type_information_from_func(func):
    function_arguments = func.args.args
    ret = []
    full = True
    for argu in function_arguments:
        if argu.annotation is not None:
            ret += [(argu.arg,argu.annotation.id)]
        else:
            ret += [(argu.arg,None)]
            full = False
    return (full,ret)




def generate_test_function(func):
    full,args = get_type_information_from_func(func)
    
    ret = []
    if full:
        annotation = '\t@hyp.given('
        lst = []
        for arg in args:
            lst += ['st.from_type(%s)' % arg[1]]
        annotation +=  ', '.join(lst) + ')'
        ret.append(annotation)
   
    
    stub = '\tdef test_%s(self,' % func.name
    lst = []
    for arg in args:
        lst += ['%s' % arg[0]]
    stub +=  ', '.join(lst) + '):'
    ret.append(stub)
    if full:
        call = '\t\tvalue = module.%s(' % (func.name)
        lst = []
        for arg in args:
            lst += ['%s' % arg[0]]
        call +=  ', '.join(lst) + ')'
        ret.append(call)

    
    

    
    

    ret.append('\t\tself.assertTrue(False)')
    ret.append('\n')
    return ret




def write_test_file(file_name,data):
    with open(file_name, 'w') as handle:
        handle.write(data)

def parse_ast(file_name):
    with open(file_name, "rt") as handle:
        return ast.parse(handle.read(), filename=file_name)


def serialize_tree_data(file_name, tree_data):
    with open(file_name, 'wb') as handle:
        pk.dump(tree_data, handle)


def un_serialize_tree_data(file_name):
    with open(file_name, 'rb') as handle:
        return pk.load(handle)
def foo(x : int, y: int):
    return x+y

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        tree = TreeData(parse_ast(filename))
        data_name = 'data_' + filename.split('.')[0] + '.pk'
        test_name = 'test_' + filename.split('.')[0] + '.py'
        if not os.path.isfile(data_name):
            serialize_tree_data(data_name, tree)
            write_test_file(test_name,tree.generate_test_file(test_name))
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




