
import main as module
import unittest as test
import hypothesis as hyp
import hypothesis.strategies as st

class Testmain(test.TestCase):

    def test_generate_test_imports(self, import_list):
        self.assertTrue(False)

    def test_get_type_information_from_func(self, func):
        self.assertTrue(False)

    def test_generate_test_function(self, func):
        self.assertTrue(False)

    def test_write_test_file(self, file_name, data):
        self.assertTrue(False)

    def test_parse_ast(self, file_name):
        self.assertTrue(False)

    def test_serialize_tree_data(self, file_name, tree_data):
        self.assertTrue(False)

    def test_un_serialize_tree_data(self, file_name):
        self.assertTrue(False)

    @hyp.given(st.from_type(int), st.from_type(int))
    def test_foo(self, x, y):
        value = module.foo(x, y)
        self.assertTrue(((x + y) == value))
if (__name__ == '__main__'):
    test.main()
