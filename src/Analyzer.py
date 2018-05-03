import glob
import os
import re



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

    def parse_function_names(self):
        """
        TODO: Parse function and method names from a java file
        """
        pass

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

def test():
    for filename, filepath, content in Analyzer().get_files_generator('download_repo/airbnb-lottie-android-c4502c1'):
        print(filename)

def test2():
    for filename, filepath, content in Analyzer().get_files_generator('download_repo/airbnb-lottie-android-c4502c1'):
        Analyzer().parse_class_names(filename, filepath, content)

if __name__ == '__main__':
    test2()
