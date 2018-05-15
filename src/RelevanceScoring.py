from elasticsearch import Elasticsearch
from src.Common import RelevanceScoringSettings
import os


class RelevanceScoring:
    def __init__(self):
        self.es = Elasticsearch([RelevanceScoringSettings.host])
        self.search_result = []
        self.run()

    def run(self):
        """
        Run relevance interface
        """
        search_string = input("Search string to evaluate: ")
        search_result = self.get_search_results(search_string)
        scored = []
        num_scored = 1
        results = search_result["hits"]["hits"]
        for res in results:
            content = res["_source"]
            doc_id = res["_id"]
            filepath = content["filepath"]
            start = content["start_row"]
            end = content["end_row"]
            print(filepath)
            print(start, end)
            document_content = self.get_document_content(filepath, start, end)
            print("-"*100)
            print(document_content)
            relevance_scoring = input("Relevance Scoring: {} of {}\
                                      \n0 Not Relevant\
                                      \n1 Marginally Relevant\
                                      \n2 Fairly Relevant\
                                      \n3 Highly Relevant\n:".format(num_scored, len(results)))
            scored.append(doc_id+","+relevance_scoring+"\n")
            num_scored += 1
            self.save_data(scored, search_string)

    def save_data(self, scored, search_string):
        """
        Saves the relevance scoring and id to file as csv
        """
        folder = RelevanceScoringSettings.relevance_scoring_folder
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, search_string)
        with open(filepath, "w") as f:
            f.writelines(scored)

    def get_document_content(self, filepath, start, end):
        """
        Opens the document with the method/class
        :return string method/class body
        """
        with open(filepath) as f:
            lines = f.readlines()
            content = ""
            for line in lines[start-1:end]:
                content += line
        return content

    def get_search_results(self, search_string):
        """
        Searches for documents on elasticsearch
        :return array of search results
        """
        search_body = self.get_json_body(search_string)
        res = self.es.search(
            index=RelevanceScoringSettings.index_used, body=search_body)
        return res

    def get_json_body(self, search_term):
        """
        Builds the json body based upon search string and category
        :return dict (json body)
        """
        json_template = RelevanceScoringSettings.search_body
        json_template["query"]["bool"]["filter"][0]["term"]["category"] = \
            RelevanceScoringSettings.category
        json_template["query"]["bool"]["must"][0]["match"]["name"]["query"] = \
            search_term
        json_template["from"] = 0
        json_template["size"] = RelevanceScoringSettings.num_to_score
        return json_template


if __name__ == "__main__":
    rs = RelevanceScoring()
