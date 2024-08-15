from app import app


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Phinehas'}
    return '''
<html>
    <head>
        <title>Home page - Genblog</title>
    </head>
    <body>
        <h1>Hello, ''' + user['username'] + '''!</h1>
    </body>
</html>'''
