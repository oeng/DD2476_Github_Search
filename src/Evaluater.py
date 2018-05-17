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
        self.relevant_documents = 100

    def run(self):
        relevance_request_body = {"requests": []}
        for filename in os.listdir(self.relevance_scoring_folder):
            evaluate_body = {}
            if not filename.startswith("."):
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
        results = self.get_precision_recall(result)
        self.plot_precision_recall(results)
        self.plot_average_precision_recall(results)

    def get_precision_recall(self, json_result):
        """
        Calculates the precision from the json_result file
        :param json_result with return json from elasticsearch
        :return dict containing arrays of precision results
        """
        results = {}
        # quality_level = json_result['quality_level']
        for key, val in json_result['details'].items():
            true_positives = 0
            precision_results = []
            recall_results = []
            for i, hit in enumerate(val['hits']):
                # print(hit['rating'])
                rating = hit['rating']
                if rating is None:
                    results[key] = {
                        'precision': precision_results, 'recall': recall_results}
                    break
                elif(rating > self.relevant_rating_threshold):
                    true_positives += 1
                results[key] = {
                    'precision': precision_results, 'recall': recall_results}
                recall_results.append(
                    true_positives/(float(self.relevant_documents)))
                precision_results.append(true_positives/float(i+1))
        return results

    def plot_average_precision_recall(self, results):
        num_results = len(results.items())
        average_prec = [0 for i in range(0, 50)]
        average_rec = [0 for i in range(0, 50)]
        for key, val in results.items():
            for i, prec in enumerate(val['precision']):
                average_prec[i] += prec
            for j, rec in enumerate(val['recall']):
                average_rec[j] += rec

        for k in range(0, len(average_prec)):
            average_prec[k] = average_prec[k]/float(num_results)
        for l in range(0, len(average_prec)):
            average_rec[l] = average_rec[l]/float(num_results)

        # Average precision
        filetype = "pdf"
        filename = "average_precision."+filetype
        fig, ax = plt.subplots()
        x = [i for i in range(0, 50)]
        ax.plot(x, average_prec)
        ax.set_ylabel("Precision")
        ax.set_title("Average Precision")
        fig.savefig(fname=os.path.join(
            self.plot_folder, filename), format=filetype, )
        plt.close('all')

        # Average recall
        filetype = "pdf"
        filename = "average_recall."+filetype
        fig, ax = plt.subplots()
        ax.plot(x, average_rec)
        ax.set_ylabel("Recall")
        ax.set_title("Average Recall")
        fig.savefig(fname=os.path.join(
            self.plot_folder, filename), format=filetype, )
        plt.close('all')

        # Average precision_recall
        filetype = "pdf"
        filename = "average_precision_recall."+filetype
        fig, ax = plt.subplots()
        ax.plot(average_rec, average_prec)
        ax.set_ylabel("Precision")
        ax.set_xlabel("Recall")
        ax.set_title("Average Precision vs Recall")
        fig.savefig(fname=os.path.join(
            self.plot_folder, filename), format=filetype, )
        plt.close('all')

    def plot_precision_recall(self, results):
        """
        Saves the fig_pures to file
        :param results dict filenames as keys containing arrays of precision and recall
        """
        filetype = "pdf"
        if not os.path.exists(self.plot_folder):
            os.makedirs(self.plot_folder)
        for key, val in results.items():
            filename = key+"_plot_precision."+filetype
            plot_path = os.path.join(
                self.plot_folder, key)
            if not os.path.exists(plot_path):
                os.makedirs(plot_path)
            # Plotting precision
            x = [i for i in range(1, len(val['precision'])+1, 1)]
            fig, ax = plt.subplots()
            ax.plot(x, val['precision'],  'bo',
                    x, val['precision'], 'b--')
            ax.set_ylabel("Precision")
            ax.set_title("Precision\n Query: " + key)
            fig.savefig(fname=os.path.join(
                plot_path, filename), format=filetype, )
            plt.close('all')

            # Plotting recall
            filename = key+"_plot_recall."+filetype
            plot_path = os.path.join(
                self.plot_folder, key)
            if not os.path.exists(plot_path):
                os.makedirs(os.path.join(plot_path))
            x = [i for i in range(1, len(val['recall'])+1, 1)]
            fig, ax = plt.subplots()
            ax.plot(x, val['recall'],  'bo', x, val['recall'], 'b--')
            ax.set_ylabel("Recall")
            ax.set_title("Recall\n Query: " + key)
            fig.savefig(fname=os.path.join(
                plot_path, filename), format=filetype, )
            plt.close('all')

            # Plot precision_recall
            filename = key+"_plot_precision_recall."+filetype
            plot_path = os.path.join(self.plot_folder, key)
            if not os.path.exists(plot_path):
                os.makedirs(os.path.join(plot_path))
            fig, ax = plt.subplots()
            ax.set_ylabel("Precision")
            ax.set_xlabel("Recall")
            ax.set_title("Precision vs Recall\n Query: " + key)
            ax.plot(val['recall'], val['precision'],  'bo',
                    val['recall'], val['precision'],  'b--')
            fig.savefig(fname=os.path.join(
                plot_path, filename), format=filetype, )
            plt.close('all')


if __name__ == "__main__":
    ev = Evaluater()
    ev.run()
    ev.plot_results()
