import elasticsearch
import datetime

es = elasticsearch.Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

def add_patent(patent_data):
    try:
        res = es.index(index="patents", document=patent_data)
        print(f"Added patent with ID: {res['_id']}")
    except Exception as e:
        print(f"Error adding patent: {e}")

patent_data = [
    {
        "_id": "1",
        "title": "A Novel Method for Improving Battery Life",
        "authors": ["John Doe", "Jane Smith"],
        "organizations": ["Acme Corp"],
        "publication_date": "2023-10-26",
        "application_date": "2022-05-15",
        "application_type": "Utility",
        "topics": ["Battery Technology", "Energy Storage"]
    },
    {
        "_id": "2",
        "title": "Improved Algorithm for Image Recognition",
        "authors": ["Peter Jones"],
        "organizations": ["Beta Inc"],
        "publication_date": "2023-09-10",
        "application_date": "2022-11-20",
        "application_type": "Utility",
        "topics": ["Artificial Intelligence", "Image Processing"]
    },
    {
        "_id": "3",
        "title": "New Design for a More Efficient Solar Panel",
        "authors": ["Alice Brown", "Bob Green"],
        "organizations": ["Gamma Ltd"],
        "publication_date": "2023-08-01",
        "application_date": "2021-12-10",
        "application_type": "Design",
        "topics": ["Solar Energy", "Renewable Energy"]
    }
]

for patent in patent_data:
    add_patent(patent)

print("Data initialization complete.")

