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

        Throws javalang.parser.JavaSyntaxError or LexerError if the file could not be parsed

        :param content: Java file content
        """
        self.tree = javalang.parse.parse(content)

        self.functions = []
        self.classes = []
        # print(tree.package.name)
        for path, node in self.tree:
            if isinstance(node, tree.ClassDeclaration):
                # attrs = ("type_parameters", "extends", "implements")
                row = node.position[0]
                f = {'name': node.name, 'row': row}
                self.classes.append(f)
            elif isinstance(node, tree.MethodDeclaration):
                if(node.return_type is not None):
                    return_type=node.return_type.name
                else:
                    return_type='void'
                # attrs = ("type_parameters", "return_type", "name", "parameters", "throws", "body")
                row = node.position[0]
                f = {'name': node.name, 'row': row, 'return_type':return_type}
                # f = {'name': node.name, 'row': row}
                self.functions.append(f)

    def get_package_name(self):
        """
        :return: File package name
        """
        if hasattr(self.tree.package, 'name'):
            return self.tree.package.name
        else:
            return None

    def get_functions(self):
        """

        :return: list of dicts
        """
        return self.functions

    def get_classes(self):
        """

        :return: list of dicts
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

