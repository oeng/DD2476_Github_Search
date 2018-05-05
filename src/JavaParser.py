import glob
from collections import namedtuple

import javalang
from javalang import tree



class JavaParser:
    def __init__(self, content):
        """
        Parse Java file content using javalang

        For tree-documentation:
        https://github.com/c2nes/javalang/blob/master/javalang/tree.py

        Throws javalang.parser.JavaSyntaxError if the file could not be parsed

        :param content: Java file content
        """
        self.tree = javalang.parse.parse(content)

        Function = namedtuple('Function', 'name row')
        Class = namedtuple('Class', 'name row')
        self.functions = []
        self.classes = []
        # print(tree.package.name)
        for path, node in self.tree:
            if isinstance(node, tree.ClassDeclaration):
                # attrs = ("type_parameters", "extends", "implements")
                row = node.position[0]
                f = Class(node.name, row)
                self.classes.append(f)
            elif isinstance(node, tree.MethodDeclaration):
                # attrs = ("type_parameters", "return_type", "name", "parameters", "throws", "body")
                row = node.position[0]
                f = Function(node.name, row)
                self.functions.append(f)

    def get_package_name(self):
        """
        :return: File package name
        """
        return self.tree.package.name

    def get_functions(self):
        """

        :return: list of named tuples
        """
        return self.functions

    def get_classes(self):
        """

        :return: list of named tuples
        """
        return self.classes


def test():
    for filepath in glob.iglob('download_repo/**/*.java', recursive=True):
        with open(filepath, 'r') as f:
            content = f.read()
        parser = JavaParser(content)
        print(parser.get_functions())


if __name__ == '__main__':
    test()

