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
            evaluate_body = {}
            with open(os.path.join(folder, filename), "r") as f:
                content = f.readlines()
            evaluate_body["request"] = self.get_request_body(filename)
            evaluate_body["ratings"] = self.get_ratings_body(content)
            evaluate_body["id"] = filename + " " + "match"
            relevance_request_body["requests"].append(evaluate_body)
        relevance_request_body["metric"] = RelevanceScoringSettings.metric
        url = RelevanceScoringSettings.host + "/" + \
            RelevanceScoringSettings.index_used + "/_rank_eval"
        response = requests.post(
            url, json=relevance_request_body)
        response_json = json.loads(response.text)
        self.handle_response(response_json)

    def handle_response(self, response):
        # TODO: Implement how we want to handle data
        folder = RelevanceScoringSettings.evaluation_result_folder
        json_filename = RelevanceScoringSettings.response_json
        if not os.path.exists(folder):
            os.makedirs(folder)
        path = os.path.join(folder, json_filename)
        with open(path, "w") as f:
            f.write(json.dumps(response))

    def get_request_body(self, filename):
        """
        :return dict, the request used for relevance scoring
        """
        query_template = {"query": {"bool": {"filter": [
            {"term": {"category": ""}}], "must": [{"match": {"name": {"query": ""}}}]}}, }

        query_template["query"]["bool"]["filter"][0]["term"]["category"] = \
            RelevanceScoringSettings.category
        query_template["query"]["bool"]["must"][0]["match"]["name"]["query"] = filename
        return query_template

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


if __name__ == "__main__":
    ev = Evaluater()
    ev.run()
