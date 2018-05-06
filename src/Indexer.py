import sys
from collections import deque

from elasticsearch import Elasticsearch, helpers

from src.Analyzer import Analyzer
# from Analyzer import Analyzer


class Indexer:
    # TODO probably use CamelCase serializer or similar for function and class names, getValue to get value
    # TODO use some serializer for package name, com.google.guava to com google guava

    def __init__(self):
        # Connection to elastic search
        # https://elasticsearch-py.readthedocs.io/en/master/api.html
        self.es = Elasticsearch()
        self.index_to_use = 'test'

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
                        'type': 'nested',
                        'filename': {'type': 'text', 'analyzer': 'camel'},
                        'filepath': {'type': 'keyword'},
                        'package': {'type': 'text', 'analyzer': 'simple'},
                        'functions': {
                            'type': 'nested',
                            'properties': {
                                'name': {'type': 'text', 'analyzer': 'camel'},
                                'row': {'type': 'integer'},
                                'return_type':{'type':'text'}
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

        # To delete existing index:
        # curl -X DELETE  'http://localhost:9200/test'

    def index_document(self, d):
        """
        Index a single document into elasticsearch

        Not use anymore
        :param d: data structure
        """

        self.es.index(
            index=self.index_to_use,
            doc_type='java',
            body=d,
        )

    def run(self):
        """
        Run the indexer

        Retrieves files from the analyzer and indexes them into elasticsearch
        """
        analyzer = Analyzer()
        # https://elasticsearch-py.readthedocs.io/en/master/helpers.html?highlight=bulk
        deque(helpers.parallel_bulk(
            self.es,
            analyzer.get_analyzed_file(),
            thread_count=4,
            index=self.index_to_use,
            doc_type='java',
            chunk_size=50
        ))
        # for d in analyzer.get_analyzed_file():
            # self.index_document(d)


if __name__ == '__main__':
    index = Indexer()
    index.run()
