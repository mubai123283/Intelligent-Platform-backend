import elasticsearch
import nltk

class Elastic:
    def __init__(self):
        self.es = elasticsearch.Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

    def _build_query(self, query_params):
        query_body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "from": (query_params['page'] - 1) * query_params['size'],
            "size": query_params['size']
        }

        if query_params.get('query'):
            query_body["query"]["bool"]["must"].append(self.nlp_query(query_params['query']))

        if query_params.get('authors'):
            query_body["query"]["bool"]["filter"].append({"terms": {"authors": query_params['authors'].split(",")}})

        if query_params.get('organizations'):
            query_body["query"]["bool"]["filter"].append({"terms": {"organizations": query_params['organizations'].split(",")}})

        if query_params.get('publication_start_date') and query_params.get('publication_end_date'):
            query_body["query"]["bool"]["filter"].append({"range": {"publication_date": {"gte": query_params['publication_start_date'], "lte": query_params['publication_end_date']}}})

        if query_params.get('application_start_date') and query_params.get('application_end_date'):
            query_body["query"]["bool"]["filter"].append({"range": {"application_date": {"gte": query_params['application_start_date'], "lte": query_params['application_end_date']}}})

        if query_params.get('application_type'):
            query_body["query"]["bool"]["filter"].append({"term": {"application_type": query_params['application_type']}})

        if query_params.get('topics'):
            query_body["query"]["bool"]["filter"].append({"terms": {"topics": query_params['topics'].split(",")}})

        return query_body

    def nlp_query(self, query):
        tokens = nltk.word_tokenize(query)
        return {
            "match": {
                "title": {
                    "query": " ".join(tokens),
                    "operator": "OR"
                }
            }
        }

    def search_patents(self, **query_params):
        query_body = self._build_query(query_params)
        result = self.es.search(index="patents", body=query_body)
        return result

    def search_by_id(self, id):
        result = self.es.get_source(index="patents", id=id)
        return result

    def count_patents_infos(self, **query_params):
        query_body = self._build_query(query_params)
        result = self.es.count(index="patents", body=query_body)
        return result["count"]
