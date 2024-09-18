from app import create_app, db
from app.models import Post
import sqlalchemy as sa

app = create_app()

with app.app_context():
    # Example operations
    from app.search import add_to_index, remove_from_index, query_index

    # Add all posts to the Elasticsearch index
    for post in db.session.scalars(sa.select(Post)):
        add_to_index('posts', post)

    # Example search query
    ids, total = query_index('posts', 'search term', 1, 10)
    print(f"Total results: {total}")
    print(f"Post IDs: {ids}")
