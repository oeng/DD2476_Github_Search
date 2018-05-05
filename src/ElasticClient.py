from datetime import datetime
from elasticsearch import Elasticsearch


class ElasticClient:
    def __init__(self):
        pass

    def test(self):
        es = Elasticsearch()

        doc = {
            'url': 'test/path',
            'function': [
                {
                    'name': 'quickSort',
                    'start': 10,
                    'end': 20,
                },
                {
                    'name': 'mergeSort',
                    'start': 30,
                    'end': 40,
                }
            ],
            'class': [
                {
                    'name': 'sortClass',
                    'start': 50,
                    'end': 60,
                },
                {
                    'name': 'compressClass',
                    'start': 80,
                    'end': 90,
                }
            ],
        }

        res = es.index(index="test-index", doc_type='java', id=1, body=doc)
        print(res['result'])

        res = es.get(index="test-index", doc_type='java', id=1)
        print(res['_source'])

        es.indices.refresh(index="test-index")

        res = es.search(index="test-index", body={"query": {"match_all": {'function':'mergeSort'}}})
        print("Got %d Hits:" % res['hits']['total'])
        # for hit in res['hits']['hits']:
            # print("%(function)s" % hit["_source"])
        print(res)


if __name__ == '__main__':
    ec = ElasticClient()
    ec.test()
