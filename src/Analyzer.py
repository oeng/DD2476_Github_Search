import glob
import os


def test():
    for filename, filepath, content in Analyzer().get_files_generator('download_repo/airbnb-lottie-android-c4502c1'):
        print(filename)


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
    
    def parse_class_names(self):
        """
        TODO: Parse class names from a java file
        """
        pass
    
    def tokens_generator(self):
        """
        TODO: Generate tokens to index for a file, return JSON object that can be used by indexer.
        """
        pass


if __name__ == '__main__':
    test()