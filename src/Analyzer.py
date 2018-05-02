def test():
    print("Hello, KTH")


class Analyzer():
    # Constructor
    def __init__(self):
        pass

    """
    TODO: Yield source code files one at a time (gustaf fixar)
    """
    def get_files_generator(self, repo_path):
        pass

    """
    TODO: Parse function and method names from a java file
    """
    def parse_function_names(self):
        pass
    
    """
    TODO: Parse class names from a java file
    """
    def parse_class_names(self):
        pass
    
    """
    TODO: Generate tokens to index for a file, return JSON object that can be used by indexer.
    """
    def tokens_generator(self):
        pass


if __name__ == '__main__':
    test()