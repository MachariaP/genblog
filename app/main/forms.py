from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l

from app import db
from app.models import User


class EditProfileForm(FlaskForm):
    """
    Form for editing user profile.
    """
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        """
        Initialize the form with the original username.

        Args:
            original_username (str): The original username of the user.
        """
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """
        Validate that the username is not already in use.

        Args:
            username (StringField): The username field to validate.

        Raises:
            ValidationError: If the username is already in use.
        """
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    """
    An empty form with only a submit button.
    """
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    """
    Form for creating a new post.
    """
    post = TextAreaField(_l('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    """
    Form for searching content.
    """
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with request arguments and disable CSRF.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    """
    Form for sending a message.
    """
    message = TextAreaField(_l('Message'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))
