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
            }
        }

        # Init index
        # self.es.indices.create(
        #     index=self.index_to_use,
        #     body=self.settings,
        #     ignore=400  # Index already exists if HTTP 400, skip exception
        # )

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

    def search_test(self):
        """
        Does not work
        # TODO
        :return:
        """
        res = self.es.search(index="test", body={
            "query": {
                "match_all": {
                    'functions.name': 'testH2CServerFallback'
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
            # self.index_document_bulk(d)
        # Run this after the for loop if using bulk
        # self.index_cache()


if __name__ == '__main__':
    index = Indexer()
    index.run()
