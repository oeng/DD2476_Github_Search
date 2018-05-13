import glob
from collections import namedtuple

import javalang
from javalang import tree

import time

class JavaParser:
    def __init__(self):
        self.tokens = ""
        self.tree = ""

        self.functions = []
        self.classes = []
        self.content = []

    def parse_separate(self, content):
        """
        Parse a Java file content using java lang, each type is saved
        separately
        Throws javalang.parser.JavaSyntaxError or LexerError if the file
        could not be parsed
        param content: Java file content
        """
        tokenizer_result = javalang.tokenizer.tokenize(content)
        self.tokens = list(tokenizer_result)
        self.tree = javalang.parser.Parser(self.tokens).parse()
        self.brace_prune_pointer = 0

        package_name = self.get_package_name()
        for path, node in self.tree:
            if isinstance(node, tree.ClassDeclaration):
                # attrs = ("type_parameters", "extends", "implements")
                start_row = node.position[0]
                end_row = self.get_end_row(start_row)
                f = {'category': "class", 'package': package_name,
                     'name': node.name, 'start_row': start_row,
                     'end_row': end_row}
                self.content.append(f)
            elif isinstance(node, tree.MethodDeclaration):
                if(node.return_type is not None):
                    return_type = node.return_type.name
                else:
                    return_type = 'void'
                start_row = node.position[0]
                # handle functions without a body
                if node.body != None:
                    end_row = self.get_end_row(start_row)
                else:
                    end_row = start_row
                f = {'category': "function", 'package': package_name, 'name': node.name,
                     'start_row': start_row, 'end_row': end_row, 'return_type': return_type}
                self.content.append(f)

    def parse(self, content):
        """
        Parse Java file content using javalang

        For tree-documentation:
        https://github.com/c2nes/javalang/blob/master/javalang/tree.py

        Throws javalang.parser.JavaSyntaxError or LexerError if the file could not be parsed

        :param content: Java file content
        """
        self.tokens = list(javalang.tokenizer.tokenize(content))
        self.tree = javalang.parse.parse(content)
        # print(tree.package.name)
        for path, node in self.tree:
            if isinstance(node, tree.ClassDeclaration):
                # attrs = ("type_parameters", "extends", "implements")
                start_row = node.position[0]
                end_row = self.get_end_row(start_row)
                f = {'name': node.name, 'start_row': start_row, 'end_row': end_row}
                self.classes.append(f)
            elif isinstance(node, tree.MethodDeclaration):
                if(node.return_type is not None):
                    return_type = node.return_type.name
                else:
                    return_type = 'void'
                # attrs = ("type_parameters", "return_type", "name", "parameters", "throws", "body")
                start_row = node.position[0]
                # handle functions without a body
                if node.body != None:
                    end_row = self.get_end_row(start_row)
                else:
                    end_row = start_row
                f = {'name': node.name, 'start_row': start_row,
                     'end_row': end_row, 'return_type': return_type}
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

    def get_content(self):
        """

        :return: list of dicts
        """
        return self.content

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
        prune_index_found = False
        for i in range(self.brace_prune_pointer, len(self.tokens)):
            token = self.tokens[i]
            line = token.position[0]
            if line >= start_row:
                # store list index for pruning
                if not prune_index_found:
                    self.brace_prune_pointer = i
                    prune_index_found = True

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
    i = 0
    parser = JavaParser()

    t0 = time.time()
    for filepath in glob.iglob('download_repo/**/*.java', recursive=True):
        with open(filepath, 'r') as f:
            content = f.read()
        parser.parse_separate(content)
        i += 1
        if i == 1000:
            break
    t1 = time.time()

    print("Items in content: %d", len(content))
    print("time : %d", t1-t0)

if __name__ == '__main__':
    test()
