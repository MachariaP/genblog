from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Phinehas'}
    return render_template('index.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
