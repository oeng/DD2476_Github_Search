from elasticsearch import Elasticsearch
from src.Analyzer import Analyzer


class Indexer:
    # TODO probably use CamelCase serializer or similar for function and class names, getValue to get value
    # TODO use some serializer for package name, com.google.guava to com google guava

    def __init__(self):
        # Connection to elastic search
        # https://elasticsearch-py.readthedocs.io/en/master/api.html
        self.es = Elasticsearch()
        self.index_to_use = 'test'
        self.bulk_cache = []

        # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-pattern-analyzer.html
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
        # Note: these settings are only taken into account for NEW indices
        self.settings = {
            'settings': {
                'analysis': {
                    'analyzer': {
                        'camel': {
                            'type': 'pattern',
                            'pattern': '([^\\p{L}\\d]+)|(?<=\\D)(?=\\d)|(?<=\\d)(?=\\D)|(?<=[\\p{L}&&[^\\p{Lu}]])(?=\\p{Lu})|(?<=\\p{Lu})(?=\\p{Lu}[\\p{L}&&[^\\p{Lu}]])'
                        }
                    }
                }
            },
            'mappings': {
                'java': {
                    'properties': {
                        'filename': {'type': 'text', 'analyzer': 'camel'},
                        'filepath': {'type': 'keyword'},
                        'package': {'type': 'text'},
                        'functions': {
                            'type': 'nested',
                            'properties': {
                                'name': {'type': 'text', 'analyzer': 'camel'},
                                'row': {'type': 'integer'}
                            },
                        },
                        'classes': {
                            'type': 'nested',
                            'properties': {
                                'name': {'type': 'text', 'analyzer': 'camel'},
                                'row': {'type': 'integer'}
                            },
                        }
                    }
                }
            }
        }

        # Init index
        self.es.indices.create(
            index=self.index_to_use,
            body=self.settings,
            ignore=400  # Index already exists if HTTP 400, skip exception
        )

    def index_document(self, d):
        """
        Index a single document into elasticsearch
        :param d: data structure
        """

        self.es.index(
            index=self.index_to_use,
            doc_type='java',
            body=d,
        )

        # print(self.es.get(index='test', doc_type='java', id=1))

    def index_document_bulk(self, d, interval=1000):
        """
        Perform bulk indexing

        Call this function as index_document, it will perform bulk indexing at certain intervals

        Note: this function will not index the last interval-1 documents.
        Call index_cache after using this function in a for loop

        :param interval: bulk index every [interval] method call
        :param d: data structure, the same as index_document
        """
        if len(self.bulk_cache) >= interval:
            # Index
            self.index_cache()
        else:
            self.bulk_cache.append(d)

    def index_cache(self):
        """
        Index all documents (if any) in the cache
        """
        if len(self.bulk_cache) > 0:
            body = {
                'index': self.bulk_cache
            }
            self.es.index(
                index=self.index_to_use,
                doc_type='java',
                body=body,
            )
            self.bulk_cache = []

    def run(self):
        """
        Run the indexer

        Retrieves files from the analyzer and indexes them into elasticsearch
        """
        analyzer = Analyzer()
        for d in analyzer.get_analyzed_file():
            self.index_document(d)
            # self.index_document_bulk(d)
        # Run this after the for loop if using bulk
        # self.index_cache()


if __name__ == '__main__':
    index = Indexer()
    index.run()
