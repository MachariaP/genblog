web: flask db upgrade; flask translate compile; gunicorn genblog:app
worker: rq worker genblog-tasks
web: flask run --host=0.0.0.0 --port=$PORT
