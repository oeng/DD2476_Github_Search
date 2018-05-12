import glob
import os
import re

import sys
import io

import javalang
import hashlib
import base64

from src.JavaParser import JavaParser


def test():
    for filename, filepath, content in Analyzer().get_files_generator('download_repo/airbnb-lottie-android-c4502c1'):
        print(filename)


def test2():
    for filename, filepath, content in Analyzer().get_files_generator('download_repo/'):
        # classes = Analyzer().parse_class_names(filename, filepath, content)
        # print(classes)
        function_names = Analyzer().parse_function_names(content)
        print(function_names)
        # package_name = Analyzer().parse_package_name(content)
        # print(package_name)


def test3():
    for filename, filepath, content in Analyzer().get_files_generator():
        content = Analyzer().remove_comments(content)
        function_names = Analyzer().parse_function_names(content)
        print(function_names)


class Analyzer:
    # Constructor
    def __init__(self):
        self.repo_path = 'download_repo'
        self.current_package = ""
        self.package_counter = 0

    def get_analyzed_file_separate(self):
        """
        Yield an analyzed file one document for each category (class, method)

        :return: dict containing: filename, filepath, package, name, return_type (method only), start_row, end_row
        """
        for filename, filepath, content in self.get_files_generator():
            try:
                parser = JavaParser()
                parser.parse_separate(content)
                # print('Analyzed file: ', filepath)
            except Exception as e:
                print(e)
                print('Warning skipping file: ', filepath, file=sys.stderr)
                continue

            # Create data strucure for elastic search here directly
            # Nested representation is handled automatically by elastic search
            # https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html
            for num, doc in enumerate(parser.get_content()):
                doc_id = filepath+str(num)
                doc_id = hashlib.md5(str.encode(doc_id)).digest()
                doc_id = base64.urlsafe_b64encode(doc_id).decode('utf-8')
                d = {
                    '_id':doc_id,
                    'filename': filename,
                    'filepath': filepath,
                    'category': doc.get('category'),
                    'name': doc.get('name'),
                    'start_row': doc.get('start_row'),
                    'end_row': doc.get('end_row'),
                    'return_type': doc.get('return_type'),
                    'package': doc.get('package'),
                    'package_id' : self.generate_package_id(doc.get('package'))
                }
                yield d

    def generate_package_id(self, package):
        if self.current_package != package:
            self.package_counter += 1
        self.current_package = package
        return self.package_counter

    def get_analyzed_file(self):
        """
        Yield an analyzed file

        :return: dict containing: filename, filepath, package, functions, classes
        """
        for filename, filepath, content in self.get_files_generator():
            try:
                parser = JavaParser()
                parser.parse(content)
                # print('Analyzed file: ', filepath)
            except Exception as e:
                print('Warning skipping file: ', filepath, file=sys.stderr)
                continue

            # Create data strucure for elastic search here directly
            # Nested representation is handled automatically by elastic search
            # https://www.elastic.co/guide/en/elasticsearch/reference/current/nested.html
            d = {
                'filename': filename,
                'filepath': filepath,
                'package': parser.get_package_name(),
                'functions': parser.get_functions(),
                'classes': parser.get_classes(),
            }
            yield d

    def get_files_generator(self):
        """
        Yield source code files one at a time

        :type repo_path: file system path to a repo containing java files
        :return tuple: (filename, filepath, content)
        """
        # Loop through all Java files in a repo
        s = os.path.sep
        for filepath in glob.iglob(self.repo_path + s + '**' + s + '*.java', recursive=True):
            filename = os.path.basename(filepath)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
            except Exception as e:
                # If the crawling was aborted, it is possible that files are corrupt
                content = ''
            yield filename, filepath, content

    def parse_package_name(self, content):
        """
        Parse file package
        :param content: Java file content
        :return: package name 'cyberdyne.skynet.vision' or None
        """

        pattern = re.compile("^package (?:\w+|\w+\.\w+)+;$")
        for line in content.split('\n'):
            if pattern.match(line):
                # We found a package declaration, strip away "package " in the beginning and ; at the end
                package_name = line[len('package '):-1]
                # Break, maximum of one package per file
                return package_name

    def remove_comments(self, content):
        """
        Replace comments with with spaces

        :param content: Java file content
        :return: content without comments
        """

        # Regex source: https://stackoverflow.com/a/2319146
        pattern = re.compile(
            '(\/\*([^*]|[\r\n]|(\*+([^*\/]|[\r\n])))*\*+\/)|(\/\/.*)')
        content = re.sub(pattern, ' ', content)
        return content

    def parse_function_names(self, content):
        """
        Find all method/function names and positions in a given text

        :type content: string
        :return list of tuple: [(function name, row)]
        """
        content = self.remove_comments(content)
        matches = []
        # Pattern for finding the start of Java functions/methods
        # TODO: Ange källa för regexet i pattern (stackoverflow), eller skriva egen version senare
        pattern = "(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])"
        for line_number, line in enumerate(content.split('\n')):
            match_iter = re.finditer(pattern, line)
            for m in match_iter:
                matched_string = m.group(0).strip()
                # Check that the parsed function/method name is not a 'new' statement
                if 'new ' in matched_string:
                    continue
                # Strip everything from matched string except function/method name
                search_obj = re.search('\\b\w+(?=\()', matched_string)
                if search_obj is None:
                    continue
                matched_string = search_obj.group(0)
                # m.start() is the end of method signature.
                # Find the end position of the entire function/method
                # end_pos = self.find_block_end(content, m.start())
                # matches.append((matched_string, m.start(), end_pos))
                matches.append((matched_string, line_number+1))
        return matches

    def find_block_end(self, content, start_pos):
        """
        Finds the end position of a method/function in a text, given the start position.

        :type content: string
        :type start_pos: integer representing the start position of a method/function in content
        :return integer: end position of the method/function
        """
        # TODO:
        end_pos = -1
        return end_pos

    def parse_class_names(self, filename, filepath, content):
        """
        Find all class names and positions in a given text

        :type content: string
        :return list of tuple: [(class name, start pos, end pos)]
        """
        classes = []
        match = re.finditer(
            r"(?:(?:(public|private|protected|static|final|abstract)\s+)*)(?:(class|interface|enum)\s+)(\w+)(((\s+)?<\s*\w+(\.\w+)*(\s*,\s*\w+(\.\w+)*\s*)*>)?)\s*((extends\s+\w+(\.\w+)*((\s+)?<.*>)?\s*)|(implements\s+(\s*(\w+(\.\w+)*((\s+)?<.*>)?)\s*,)*\s*(\w+(\.\w+)*((\s+)?<.*>)?)\s*))*(?={)", content)

        valid_format, end_row = Analyzer().check_brace_balance(filename, filepath, content)

        if valid_format:
            for m in match:
                classes.append((m.group(2), m.start(), end_row))
        else:
            print(":parse_class_names: found misaligned parantheses, skipping file")

        if end_row > -1 and not classes:
            print(filepath + filename)

        return classes

    def check_brace_balance(self, filename, filepath, content):
        """
        Checks content for balanced braces while keeping content untouched.
        Reads per line for storage of row in index.
        Handles (), {} and /* */.

        :type content: string
        :return bool: True if braces are balanced TODO:
        """

        stack = []
        row = 0
        ignore_braces = False
        it = iter(io.StringIO(content).readlines())

        while True:
            try:
                row += 1
                line = next(it)
                char_it = iter(line)
                prev_c = ''
                while True:
                    try:
                        c = next(char_it)

                        # Ignore while inside multirow comment
                        if c == '/' and prev_c != ':':
                            c = next(char_it)
                            # multirow comment
                            if c == '*':
                                ignore_braces = True
                            elif c == '/':
                                break

                        # Start reading in braces when outside of comment again
                        if c == '*':
                            c = next(char_it)
                            if c == '/':
                                ignore_braces = False

                        if not ignore_braces:
                            try:
                                # Matching on left-side brace. Add to stack
                                if c == '(' or c == '{':
                                    stack.append(c)
                                # Matching of right-side ). Pop stack
                                if c == ')':
                                    if stack[-1] == '(':
                                        stack.pop()
                                        # If matching paranthesis found and stack is empty, we have found end of block
                                        if len(stack) == 0:
                                            return True, row
                                    else:
                                        print("\nBad format: " +
                                              filepath + filename)
                                        print(
                                            "Line %s: found (), whould have been {}" % row)
                                        return False, -1
                                # Matching of right-side }. Pop stack
                                if c == '}':
                                    if stack[-1] == '{':
                                        stack.pop()
                                        # If matching paranthesis found and stack is empty, we have found end of block
                                        if len(stack) == 0:
                                            return True, row
                                    else:
                                        print("\nBad format: " +
                                              filepath + filename)
                                        print(
                                            "Line %s: found (), whould have been {}" % row)
                                        return False, -1
                            except IndexError:
                                print("\nBad format: " + filepath + filename)
                                print(
                                    "Line %s: pop on empty stack. Uneven braces." % row)
                                return False, -1
                        prev_c = c
                    except StopIteration:
                        break

            except StopIteration:
                break

        # Make sure stack is empty
        if not stack:
            print("File ok.")
            return True, -1
        else:
            print("\nBad format: " + filepath + filename)
            print("Line %s: [EOF]" % row)
            return False, -1

    def tokens_generator(self):
        """
        TODO: Generate tokens to index for a file, return JSON object that can be used by indexer.
        """
        pass


if __name__ == '__main__':
    test3()
