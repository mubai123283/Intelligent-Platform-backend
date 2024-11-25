from flask import Flask, request, jsonify
from flask_cors import CORS
from service.elastic import Elastic
app = Flask(__name__)
CORS(app)
elastic = Elastic()
def parse_filters(filter_string):
    """Parses the filter string into a dictionary of filters."""
    filters = {}
    if filter_string:
        for filter_item in filter_string.split(','):
            key, value = filter_item.split(':', 1)
            filters[key] = value
    return filters

@app.route('/searchPatents', methods=['GET'])
def search_patents():
    query_params = request.args.to_dict(flat=True)
    query_params['page'] = int(query_params.get('page', 1))
    query_params['size'] = int(query_params.get('size', 10))

    filters = parse_filters(query_params.pop('filter', ''))
    query = query_params.get('query', '')
    for key, value in filters.items():
        if key == 'title':
            query = f"({query} AND title:{value})" if query else f"title:{value}"
        elif key == 'author':
            query_params['authors'] = f"{query_params.get('authors','')},{value}".strip(',')
        elif key == 'organization':
            query_params['organizations'] = f"{query_params.get('organizations','')},{value}".strip(',')
        elif key == 'publication_date':
            start_date, end_date = value.split('-')
            query_params['publication_start_date'] = start_date
            query_params['publication_end_date'] = end_date
        elif key == 'application_date':
            start_date, end_date = value.split('-')
            query_params['application_start_date'] = start_date
            query_params['application_end_date'] = end_date
        elif key == 'topic':
            query_params['topics'] = f"{query_params.get('topics','')},{value}".strip(',')

    query_params['query'] = query
    result = elastic.search_patents(**query_params)
    return jsonify({'total': result['hits']['total']['value'], 'items': result['hits']['hits']})
@app.route('/getPatentById', methods=['GET'])
def get_patent_by_id():
    patent_id = request.args.get('_id')
    if not patent_id:
        return jsonify({'error': 'Missing patent ID'}), 400
    result = elastic.search_by_id(patent_id)
    return jsonify(result)

@app.route('/countPatentsInfos', methods=['GET'])
def count_patents_infos():
    query_params = request.args.to_dict(flat=True)
    result = elastic.count_patents_infos(**query_params)
    return jsonify({'count': result})

if __name__ == '__main__':
    app.run(debug=True)
