from flask import current_app


def add_to_index(index, model):
    """
    Add a model instance to the Elasticsearch index.

    Args:
        index (str): The name of the index.
        model (Model): The model instance to index.
    """
    if not current_app.elasticsearch:
        return
    payload = {field: getattr(model, field) for field in model.__searchable__}
    try:
        current_app.elasticsearch.index(
                index=index, id=model.id, document=payload)
    except Exception as e:
        current_app.logger.error(f"Elasticsearch indexing error: {e}")


def remove_from_index(index, model):
    """
    Remove a model instance from the Elasticsearch index.

    Args:
        index (str): The name of the index.
        model (Model): The model instance to remove.
    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    """
    Query the Elasticsearch index.

    Args:
        index (str): The name of the index.
        query (str): The search query.
        page (int): The page number.
        per_page (int): The number of results per page.

    Returns:
        tuple: A tuple containing the list of IDs, the total count of results.
    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page
    )
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
