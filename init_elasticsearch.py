from elasticsearch import Elasticsearch

def create_index(es, index_name):
    # Define the index mapping
    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "body": {"type": "text"},
                "author": {"type": "keyword"},
                "timestamp": {"type": "date"}
            }
        }
    }
    
    # Create the index
    es.indices.create(index=index_name, body=mapping)

if __name__ == "__main__":
    # Replace 'localhost:9200' with your Elasticsearch host URL if different
    es = Elasticsearch(hosts=["http://localhost:9200"])
    index_name = "post"
    
    if not es.indices.exists(index=index_name):
        create_index(es, index_name)
        print(f"Index '{index_name}' created.")
    else:
        print(f"Index '{index_name}' already exists.")
