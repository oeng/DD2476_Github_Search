from elasticsearch import Elasticsearch
from src.Common import RelevanceScoringSettings
import os
import requests
import json


class Evaluater:
    def __init__(self):
        self.es = Elasticsearch(
            RelevanceScoringSettings.host+"/_rank_eval", send_get_body_as="POST")

    def run(self):
        folder = RelevanceScoringSettings.folder
        relevance_request_body = {}
        relevance_request_body["requests"] = []
        for filename in os.listdir(folder):
            with open(os.path.join(folder, filename), "r") as f:
                content = f.readlines()
                request_body = self.get_request_body(filename)
                ratings_body = self.get_ratings_body(content)
                request_body["ratings"] = ratings_body
                relevance_request_body["requests"].append(request_body)
        relevance_request_body['metric'] = RelevanceScoringSettings.metric
        url = RelevanceScoringSettings.host+"/" + \
            RelevanceScoringSettings.index_used + "/_rank_eval"
        response = requests.post(
            url, json=relevance_request_body)
        response_json = json.loads(response.text)
        self.handle_response(response_json)

    def handle_response(self, response):
        # TODO: Implement how we want to handle data
        print(response['quality_level'])
    def get_request_body(self, filename):
        """
        :return dict, the request used for relevance scoring
        """
        query_template = RelevanceScoringSettings.search_body
        query_template["query"]["bool"]["filter"][0]["term"]["category"] = \
            RelevanceScoringSettings.category
        query_template["query"]["bool"]["must"][0]["match"]["name"]["query"] = \
            filename
        request = {}
        request["id"] = filename + " " + "match"
        request["request"] = query_template
        return request

    def get_ratings_body(self, content):
        """
        Gets the rating based upon the elasticsearch format
        :return array of dictionary ratings
        """
        ratings = []
        for pair in content:
            splitted = pair.split(",")
            doc_id = splitted[0]
            rating = splitted[1].strip()
            ratings.append(
                {"_index": RelevanceScoringSettings.index_used, "_id": doc_id, "rating": rating})
        return ratings

    def get_evaluated(self):
        """
        :return array of evaluated search terms
        """
        return ""


if __name__ == "__main__":
    ev = Evaluater()
    ev.run()
