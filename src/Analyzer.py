import glob
import os
import sys
import hashlib
import base64

from src.JavaParser import JavaParser


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

