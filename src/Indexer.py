from elasticsearch import Elasticsearch
from src.Analyzer import Analyzer


class Indexer:
    def __init__(self):
        # Connection to elastic search
        # https://elasticsearch-py.readthedocs.io/en/master/api.html
        self.es = Elasticsearch()

    def index_document(self, d):
        """
        Index a document into elasticsearch
        :param d: data structure
        """

        # TODO maybe perform batch requests instead to elasticsearch, avoids possible slow HTTP overhead
        # https://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers

        # TODO probably use CamelCase serializer or similar for function and class names, getValue to get value
        # TODO use some serializer for package name, com.google.guava to com google guava

        self.es.index(
            index='test',
            doc_type='java',
            body=d,
        )

        # print(self.es.get(index='test', doc_type='java', id=1))

    def search_test(self):
        res = self.es.search(index="test", body={
            "query": {
                "match_all": {
                    'function': 'mergeSort'
                }
            }
        })
        print(res)

    def run(self):
        """
        Run the indexer

        Retrieves files from the analyzer and indexes them into elasticsearch
        """
        analyzer = Analyzer()
        for d in analyzer.get_analyzed_file():
            self.index_document(d)
            self.search_test()
            break


if __name__ == '__main__':
    index = Indexer()
    index.run()
