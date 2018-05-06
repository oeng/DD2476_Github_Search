from elasticsearch import Elasticsearch


def search_test():
    # Nice examples if using Python: https://github.com/elastic/elasticsearch-py/blob/master/example/queries.py

    es = Elasticsearch()
    res = es.search(
        index='test',
        doc_type='java',
        body={
            'query': {
                'match': {
                    'package': 'internal'
                }
            }
        })
    print(res)


if __name__ == '__main__':
    search_test()
