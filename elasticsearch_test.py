from elasticsearch import Elasticsearch

# Create a connection to Elasticsearch
es = Elasticsearch('http://localhost:9200')

# Index a document
es.index(index='my_index', id=1, document={'text': 'this is a test'})
es.index(index='my_index', id=2, document={'text': 'a second test'})

# Search for documents
result = es.search(index='my_index', query={'match': {'text': 'this test'}})
print(result)

# Delete an index
es.indices.delete(index='my_index')
