import os


class RelevanceScoringSettings:
    index_used = "github_search"
    host = "http://localhost:9200"
    category = "function"
    response_json = 'evaluation_response.json'
    evaluation_result_folder = "evaluation_results"
    relevance_scoring_folder = os.path.join(
        evaluation_result_folder, "relevance_scoring_results")
    plot_folder = os.path.join(evaluation_result_folder, "plots")
    relevant_rating_threshold = 1
    num_to_score = 50
    # The search settings to be evaluated
    search_body = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {
                        "category": ""
                    }
                    }
                ],
                "must": [
                    {
                        "match": {
                            "name": {
                                "query": ""
                            }
                        }
                    }
                ]
            }
        },
    }
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html
    evaluate_body = {
        "requests": [
            {
                # "id": "",
                # "request": {
                # "query": {"match": {"text": "amsterdam"}}
                # },

                # "ratings": [
                # {"_index": "my_index", "_id": "doc3", "rating": 1}
                # ]
            }
            # , {...}
        ]
    }

    # TODO: Implement more performance evaluations
    metric = {
        "precision": {
            "k": num_to_score,
            "relevant_rating_threshold": relevant_rating_threshold,
            "ignore_unlabeled": "false"
        }
    }


class IndexSettings:
    settings = {}
    settings_separate = {}
    analyzer = {
        "analysis": {
            "analyzer": {
                "camel": {
                    "type": "pattern",
                    "pattern": "([^\\p{L}\\d]+)|(?<=\\D)(?=\\d)|(?<=\\d)(?=\\D)|(?<=[\\p{L}&&[^\\p{Lu}]])(?=\\p{Lu})|(?<=\\p{Lu})(?=\\p{Lu}[\\p{L}&&[^\\p{Lu}]])"
                }
            }
        }
    }

    # www.elastic.co/guide/en/elasticsearch/reference/current/analysis-pattern-capture-tokenfilter.html
    analyzer_pattern_capture = {
        "analysis": {
            "analyzer": {
                "camel": {
                    "tokenizer": "pattern",
                    "filter": ["camel_pattern", "lowercase"]
                }
            },
            "filter": {
                "camel_pattern": {
                    "type": "pattern_capture",
                    "preserve_original": True,
                    "patterns": ["(\\p{Ll}+|\\p{Lu}\\p{Ll}+|\\p{Lu}+)",
                                 "(\\d+)"]
                }
            }
        }
    }

    mappings = {"mappings": {
        "java": {
            "properties": {
                # "type": "nested", # Tror denna måste bort för att
                # dokumenten ska bli nested.
                "filename": {"type": "text", "analyzer": "camel"},
                "filepath": {"type": "keyword"},
                "package": {"type": "text", "analyzer": "simple"},
                "functions": {
                    "type": "nested",
                    "properties": {
                            "name": {"type": "text", "analyzer": "camel"},
                            "start_row": {"type": "integer"},
                            "end_row": {"type": "integer"},
                            "return_type": {"type": "text"},
                    },
                },
                "classes": {
                    "type": "nested",
                    "properties": {
                            "name": {"type": "text", "analyzer": "camel"},
                            "start_row": {"type": "integer"},
                            "end_row": {"type": "integer"},
                    },
                }
            }
        }
    }
    }
    """
    Similarity can be one of BM25, classic, boolean
    BM25 is Elasticsearch default similarity measure.
    classic is regular tf-idf.
    boolean: score should only be based on whether the query terms match or not. Boolean similarity
    gives terms a score equal to their query boost.
    """
    mappings_separate = {
        "java": {
            "properties": {
                "category": {"type": "keyword"},
                "filepath": {"type": "keyword"},
                "package": {"type": "text", "fielddata": "true", "analyzer": "camel",
                            "fields": {"raw": {"type": "keyword"}}},
                "package_id": {"type": "integer"},
                "name": {"type": "text", "analyzer": "camel", "similarity": "BM25"},
                "start_row": {"type": "integer"},
                "end_row": {"type": "integer"},
                "return_type": {"type": "text"},
            },
        }
    }
    settings["settings"] = analyzer
    settings["mapping"] = mappings
    settings_separate["settings"] = analyzer_pattern_capture
    settings_separate["mappings"] = mappings_separate
