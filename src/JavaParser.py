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
        self.tokens = list(javalang.tokenizer.tokenize(content))
        self.tree = javalang.parse.parse(content)

        self.functions = []
        self.classes = []
        # print(tree.package.name)
        for path, node in self.tree:
            if isinstance(node, tree.ClassDeclaration):
                # attrs = ("type_parameters", "extends", "implements")
                start_row = node.position[0]
                end_row = self.get_end_row(start_row);
                f = {'name': node.name, 'start_row': start_row, 'end_row': end_row}
                self.classes.append(f)
            elif isinstance(node, tree.MethodDeclaration):
                if(node.return_type is not None):
                    return_type=node.return_type.name
                else:
                    return_type='void'
                # attrs = ("type_parameters", "return_type", "name", "parameters", "throws", "body")
                start_row = node.position[0]
                # handle functions without a body
                if node.body != None:
                    end_row = self.get_end_row(start_row)
                else:
                    end_row = start_row
                f = {'name': node.name, 'start_row': start_row, 'end_row': end_row, 'return_type':return_type}
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

    def get_end_row(self, start_row):
        """
        Finds end row of body declaration of classes and methods

        TODO: Optimize. Iterates from start of set of token.
              Slim down to start iterate at start_row

        :param: starting row
        :return: end row
        """
        balance = 0
        line = -1
        for token in self.tokens:
            line = token.position[0]
            if line >= start_row:
                if token.__class__.__name__ == 'Separator' and token.value == '{':
                    balance += 1
                if token.__class__.__name__ == 'Separator' and token.value == '}':
                    balance -= 1
                    if balance == 0:
                        return line
                if balance < 0:
                    print("unbalanced")
                    print(start_row, line)
                    raise Exception("unbalanced")
        # return last line
        return line

def test():
    for filepath in glob.iglob('download_repo/**/*.java', recursive=True):
        with open(filepath, 'r') as f:
            content = f.read()
        parser = JavaParser(content)
        print(parser.get_functions())



if __name__ == '__main__':
    test()
