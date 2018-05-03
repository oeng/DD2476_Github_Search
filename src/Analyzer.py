import glob
import os
import re

import sys
import io

def test():
    for filename, filepath, content in Analyzer().get_files_generator('download_repo/airbnb-lottie-android-c4502c1'):
        print(filename)

def test2():
    for filename, filepath, content in Analyzer().get_files_generator('download_repo/airbnb-lottie-android-c4502c1'):
        Analyzer().parse_class_names(filename, filepath, content)


class Analyzer():
    # Constructor
    def __init__(self):
        pass

    def get_files_generator(self, repo_path):
        """
        Yield source code files one at a time

        :type repo_path: file system path to a repo containing java files
        :return tuple: (filename, filepath, content)
        """
        # Loop through all Java files in a repo
        s = os.path.sep
        for filepath in glob.iglob(repo_path + s + '**' + s + '*.java', recursive=True):
            filename = os.path.basename(filepath)
            with open(filepath, 'r') as f:
                content = f.read()
            yield filename, filepath, content

    def parse_function_names(self, content):
        """
        Find all method/function names and positions in a given text

        :type content: string
        :return list of tuple: [(method/function name, start pos, end pos)]
        """
        matches = []
        # Pattern for finding the start of Java functions/methods
        # TODO: Ange källa för regexet i pattern (stackoverflow), eller skriva egen version senare
        pattern = "(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])"
        match_iter = re.finditer(pattern, content)
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
            end_pos = self.find_block_end(content, m.start())
            matches.append((matched_string, m.start(), end_pos))
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
        match = re.finditer(r"(?:(?:(public|private|protected|static|final|abstract)\s+)*)" +
                              "(?:class\s+)(\w+)\s*((extends\s+\w+\s*)|(implements\s+(\s*\w+\s*,)*\s*\w+\s*))*(?={)", content)
        for m in match:
            if(Analyzer().check_brace_balance(filename, filepath, content)):
                classes.append((m.group(2),m.start(),m.end()))
        return classes

    def check_brace_balance(self, filename, filepath, content, ):
        """
        Checks content for balanced braces while keeping content untouched.
        Reads per line for storage of row in index.
        Handles (), {} and /* */.

        :type content: string
        :return bool: True if braces are balanced TODO:
        """

        stack = []
        row = 0
        ignore_braces = False;
        it = iter(io.StringIO(content).readlines())

        while True:
            try:
                row += 1
                line = next(it)
                char_it = iter(line)
                while True:
                    try:
                        c = next(char_it)

                        # Ignore while inside multirow comment
                        if re.match(r'\/',c):
                            c = next(char_it)
                            # multirow comment
                            if re.match(r'\*',c):
                                ignore_braces = True
                            if re.match(r'\/',c):
                                break

                        # Start reading in braces when outside of comment again
                        if re.match(r'\*',c):
                            c = next(char_it)
                            if re.match(r'\/',c):
                                ignore_braces = False;


                        if not ignore_braces:
                            try:
                                # Matching on left-side brace. Add to stack
                                if re.match(r'\(|{',c):
                                    stack.append(c)
                                # Matching of right-side ). Pop stack
                                if re.match(r'\)',c):
                                    if stack[-1] == '(':
                                        stack.pop()
                                    else:
                                        print("\nBad format: " + filepath + filename)
                                        print("Line %s: found (), whould have been {}" % row)
                                        return False
                                # Matching of right-side }. Pop stack
                                if re.match(r'}',c):
                                    if stack[-1] == '{':
                                        stack.pop()
                                    else:
                                        print("\nBad format: " + filepath + filename)
                                        print("Line %s: found (), whould have been {}" % row)
                                        return False
                            except IndexError:
                                print("\nBad format: " + filepath + filename)
                                print("Line %s: pop on empty stack. Uneven braces." % row)
                                return False
                    except StopIteration:
                        break;

            except StopIteration:
                break

        # Make sure stack is empty
        if not stack:
            print("File ok.")
            return True;
        else:
            print("\nBad format: " + filepath + filename)
            print("Line %s: [EOF]" % row)
            return False;

    def tokens_generator(self):
        """
        TODO: Generate tokens to index for a file, return JSON object that can be used by indexer.
        """
        pass


if __name__ == '__main__':
    test2()
