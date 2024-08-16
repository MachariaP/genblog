from flask import render_template, flash, redirect, url_for
from app import app, db
from app.models import User
import sqlalchemy as sa
from flask_login import logout_user
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Phinehas'}
    posts = [
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland!'
                },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was so cool!'
                }
            ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    Returns:
        Response:
            Redirects to the index page if the user is authenticated or login
            is successful.
            Otherwise, renders the login template with the login form.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
                sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """
    Log out the current user and redirect to the index page.
    """
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
