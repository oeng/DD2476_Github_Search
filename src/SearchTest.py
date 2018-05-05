from elasticsearch import Elasticsearch


def search_test():
    es = Elasticsearch()
    res = es.search(
        index='test',
        doc_type='java',
        body={
            'query': {
                'match': {
                    'package': 'okhttp3'
                }
            }
        })
    print(res)


if __name__ == '__main__':
    search_test()
