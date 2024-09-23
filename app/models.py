from datetime import datetime, timezone
from hashlib import md5
import json
from time import time
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import redis
import rq

from app import db, login
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin:
    """
    Mixin class to add search functionality to SQLAlchemy models.
    """
    @classmethod
    def search(cls, expression, page, per_page):
        """
        Search for records matching the given expression.

        Args:
            expression (str): The search expression.
            page (int): The page number.
            per_page (int): The number of records per page.

        Returns:
            tuple: A tuple containing the list of records and the total count.
        """
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = [(ids[i], i) for i in range(len(ids))]
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total

    @classmethod
    def before_commit(cls, session):
        """
        Store changes before committing the session.

        Args:
            session (Session): The SQLAlchemy session.
        """
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        """
        Update the search index after committing the session.

        Args:
            session (Session): The SQLAlchemy session.
        """
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        """
        Reindex all records of the model.
        """
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey(
        'user.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey(
        'user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """
    User model for storing user details and authentication.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
            sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(
            sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] =
    so.mapped_column(default=lambda: datetime.now(timezone.utc))
    last_message_read_time: so.Mapped[Optional[datetime]]

    posts: so.WriteOnlyMapped['Post'] =
    so.relationship(back_populates='author')
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
    messages_sent: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.sender_id', back_populates='author')
    messages_received: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.recipient_id', back_populates='recipient')
    notifications: so.WriteOnlyMapped[
            'Notification'] = so.relationship(back_populates='user')
    tasks: so.WriteOnlyMapped['Task'] = so.relationship(back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """
        Set the user's password.

        Args:
            password (str): The password to set.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check the user's password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """
        Generate the user's avatar URL.

        Args:
            size (int): The size of the avatar.

        Returns:
            str: The URL of the avatar.
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        """
        Follow another user.

        Args:
            user (User): The user to follow.
        """
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        """
        Unfollow another user.

        Args:
            user (User): The user to unfollow.
        """
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        """
        Check if the user is following another user.

        Args:
            user (User): The user to check.

        Returns:
            bool: True if a user is following the other user, False otherwise.
        """
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        """
        Get the count of followers.

        Returns:
            int: The count of followers.
        """
        query = sa.select(sa.func.count()).select_from(
                self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        """
        Get the count of users being followed.

        Returns:
            int: The count of users being followed.
        """
        query = sa.select(sa.func.count()).select_from(
                self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        """
        Get the posts from users being followed.

        Returns:
            Query: The query for the posts.
        """
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(Follower.id == self.id, Author.id == self.id))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

    def get_reset_password_token(self, expires_in=600):
        """
        Generate a token for resetting the password.

        Args:
            expires_in (int): The expiration time of the token in seconds.

        Returns:
            str: The generated token.
        """
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        """
        Verify the password reset token.

        Args:
            token (str): The token to verify.

        Returns:
            User: The user associated with the token, or None if invalid.
        """
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return db.session.get(User, id)

    def unread_message_count(self):
        """
        Get the count of unread messages.

        Returns:
            int: The count of unread messages.
        """
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        query = sa.select(Message).where(Message.recipient == self,
                                         Message.timestamp > last_read_time)
        return db.session.scalar(sa.select(
            sa.func.count()).select_from(query.subquery()))

    def add_notification(self, name, data):
        """
        Add a notification for the user.

        Args:
            name (str): The name of the notification.
            data (dict): The data of the notification.

        Returns:
            Notification: The created notification.
        """
        db.session.execute(self.notifications.delete().where(
            Notification.name == name))
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def launch_task(self, name, description, *args, **kwargs):
        """
        Launch a background task.

        Args:
            name (str): The name of the task.
            description (str): The description of the task.
            *args: Additional arguments for the task.
            **kwargs: Additional keyword arguments for the task.

        Returns:
            Task: The created task.
        """
        rq_job = current_app.task_queue.enqueue(
                f'app.tasks.{name}', self.id, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name,
                    description=description, user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        """
        Get the tasks in progress.

        Returns:
            Query: The query for the tasks in progress.
        """
        query = self.tasks.select().where(not Task.complete)
        return db.session.scalars(query)

    def get_task_in_progress(self, name):
        """
        Get a specific task in progress.

        Args:
            name (str): The name of the task.

        Returns:
            Task: The task in progress, or None if not found.
        """
        query = self.tasks.select().where(
                Task.name == name, not Task.complete)
        return db.session.scalar(query)


@login.user_loader
def load_user(id):
    """
    Load a user by ID.

    Args:
        id (int): The ID of the user.

    Returns:
        User: The user object.
    """
    return db.session.get(User, int(id))


class Post(SearchableMixin, db.Model):
    """
    Post model for storing user posts.
    """
    __searchable__ = ['body']
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
            index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(User.id), index=True)
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Message(db.Model):
    """
    Message model for storing user messages.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    sender_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(User.id), index=True)
    recipient_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(User.id), index=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
            index=True, default=lambda: datetime.now(timezone.utc))

    author: so.Mapped[User] = so.relationship(
            foreign_keys='Message.sender_id',
            back_populates='messages_sent')
    recipient: so.Mapped[User] = so.relationship(
            foreign_keys='Message.recipient_id',
            back_populates='messages_received')

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    """
    Notification model for storing user notifications.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    user_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(User.id), index=True)
    timestamp: so.Mapped[float] = so.mapped_column(index=True, default=time)
    payload_json: so.Mapped[str] = so.mapped_column(sa.Text)

    user: so.Mapped[User] = so.relationship(back_populates='notifications')

    def get_data(self):
        """
        Get the data of the notification.

        Returns:
            dict: The data of the notification.
        """
        return json.loads(str(self.payload_json))


class Task(db.Model):
    """
    Task model for storing background tasks.
    """
    id: so.Mapped[str] = so.mapped_column(sa.String(36), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))
    complete: so.Mapped[bool] = so.mapped_column(default=False)

    user: so.Mapped[User] = so.relationship(back_populates='tasks')

    def get_rq_job(self):
        """
        Get the RQ job associated with the task.

        Returns:
            Job: The RQ job, or None if not found.
        """
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        """
        Get the progress of the task.

        Returns:
            int: The progress of the task as a percentage.
        """
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
