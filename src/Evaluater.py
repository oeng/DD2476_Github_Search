from elasticsearch import Elasticsearch
from src.Common import RelevanceScoringSettings
import os
import requests
import json
import matplotlib.pyplot as plt


class Evaluater:
    def __init__(self):
        self.es = Elasticsearch(
            RelevanceScoringSettings.host+"/_rank_eval", send_get_body_as="POST")
        self.relevance_scoring_folder = RelevanceScoringSettings.relevance_scoring_folder
        self.evaluation_folder = RelevanceScoringSettings.evaluation_result_folder
        self.index_used = RelevanceScoringSettings.index_used
        self.response_json = RelevanceScoringSettings.response_json
        self.host = RelevanceScoringSettings.host
        self.metric = RelevanceScoringSettings.metric
        self.relevant_rating_threshold = RelevanceScoringSettings.relevant_rating_threshold
        self.plot_folder = RelevanceScoringSettings.plot_folder

    def run(self):
        relevance_request_body = {}
        relevance_request_body["requests"] = []
        for filename in os.listdir(self.relevance_scoring_folder):
            evaluate_body = {}
            with open(os.path.join(self.relevance_scoring_folder, filename), "r") as f:
                content = f.readlines()
            evaluate_body["request"] = self.get_request_body(filename)
            evaluate_body["ratings"] = self.get_ratings_body(content)
            evaluate_body["id"] = filename
            relevance_request_body["requests"].append(evaluate_body)
        relevance_request_body["metric"] = self.metric
        url = self.host + "/" + \
            self.index_used + "/_rank_eval"
        response = requests.post(
            url, json=relevance_request_body)
        response_json = json.loads(response.text)
        self.handle_response(response_json)

    def handle_response(self, response):
        # TODO: Implement how we want to handle data
        json_filename = self.response_json
        if not os.path.exists(self.evaluation_folder):
            os.makedirs(self.evaluation_folder)
        path = os.path.join(self.evaluation_folder, json_filename)
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
                {"_index": self.index_used, "_id": doc_id, "rating": rating})
        return ratings

    def plot_results(self):
        """
        Plots the result after reading it from the json_result
        """
        json_path = os.path.join(self.evaluation_folder, self.response_json)
        with open(json_path, 'r') as f:
            result = json.loads(f.read())
        results = self.get_precision(result)
        self.plot_precision(results)

    def get_precision(self, json_result):
        """
        Calculates the precision from the json_result file
        :param json_result with return json from elasticsearch
        :return dict containing arrays of precision results
        """
        results = {}
        # quality_level = json_result['quality_level']
        for key, val in json_result['details'].items():
            # relevant_docs_retrieved = val['metric_details']['relevant_docs_retrieved']
            # docs_retrieved = val['metric_details']['docs_retrieved']
            sum_relevant = 0
            precision_results = []
            for i, hit in enumerate(val['hits']):
                # print(hit['rating'])
                rating = hit['rating']
                if rating is None:
                    results[key] = precision_results
                    break
                elif(rating > self.relevant_rating_threshold):
                    sum_relevant += 1
                if i % 10 == 9 and i != 0:
                    precision_results.append(sum_relevant/float(i+1))
        return results

    def plot_precision(self, results):
        """
        Saves the figures to file
        :param results dict filenames as keys containing arrays of precision
        """
        filetype = "pdf"
        if not os.path.exists(self.plot_folder):
            os.makedirs(self.plot_folder)
        for key, val in results.items():
            plot_path = os.path.join(
                self.plot_folder, key+"_plot."+filetype)
            x = [i for i in range(10, len(val)*10+10, 10)]
            fig, ax = plt.subplots()
            ax.plot(x, val,  'bo', x, val, 'bj-')
            ax.set_xticks(x)
            ax.set_ylabel("Precision")
            ax.set_title("Query: " + key)
            fig.savefig(fname=plot_path, format=filetype, )


if __name__ == "__main__":
    ev = Evaluater()
    ev.run()
    ev.plot_results()
