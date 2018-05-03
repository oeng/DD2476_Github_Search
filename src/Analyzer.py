import glob
import os
import re


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
        matches = []
        # Pattern for finding the start of Java functions/methods
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
        end_pos = -1
        return end_pos

    def parse_class_names(self, filename, filepath, content):
        """
        TODO: Parse class names from a java file
        """
        classes = []
        match = re.finditer(r"(?:(?:(public|private|protected|static|final|abstract)\s+)*)" +
                              "(?:class\s+)(\w+)\s*((extends\s+\w+\s*)|(implements\s+(\s*\w+\s*,)*\s*\w+\s*))*(?={)", content)
        for m in match:
            classes.append((m.group(2),m.start(),m.end()))
        return classes

    def tokens_generator(self):
        """
        TODO: Generate tokens to index for a file, return JSON object that can be used by indexer.
        """
        pass


if __name__ == '__main__':
    test2()
