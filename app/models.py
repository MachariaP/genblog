from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import login, db
from flask_login import UserMixin


followers = sa.Table(
        'followers',
        db.metadata,
        sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
                  primary_key=True),
        sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
                  primary_key=True)
        )


class User(UserMixin, db.Model):
    """
    Represents a user in the application.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password_hash (Optional[str]): The hashed password of the user.
        posts (WriteOnlyMapped[Post]): The posts authored by the user.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
            sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(
            sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(104))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
            default=lambda: datetime.now(timezone.utc))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
            back_populates='author')
    following: so.WriteOnlyMapped['User'] = so.relationship(
            secondary=followers, primaryjoin=(followers.c.follower_id == id),
            secondaryjoin=(followers.c.followed_id == id),
            back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
            secondary=followers, primaryjoin=(followers.c.followed_id == id),
            secondaryjoin=(followers.c.follower_id == id),
            back_populates='following')



    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password: str) -> None:
        """Hash and set the user's password.

        Args:
            password (str): The password to hash and set.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check the user's password against the stored hash.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches the hash, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        """
        Follows the specified user.

        Args:
            user (User): The user to follow.
        """
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        """
        Unfollows the specified user.

        Args:
            user (User): The user to unfollow.

        Returns:
            None
        """
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        """
        Checks if the current user is following the specified user.

        Args:
            user (User): The user to check.

        Return:
            int: The number of followers.
        """
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        """
        Returns the number of users the current user is following.

        Returns:
            int: The number of users the current user is following.
        """
        query = sa.select(sa.func.count()).select_from(
                self.following.select().subquery())
        return db.session.scalar(query)


@login.user_loader
def load_user(id):
    """
    Load a user from the database by user ID.

    The function is used by Flask-Login to reload the user object from the
    user ID stored in the session.
    It is decorated with '@login.user_loader' to register
    it as the user loader callback.

    Args:
        id (str): The user ID stored in the session.
            Flask-Login passes this as a string.

    Returns:
        User: The User object corresponding to the given ID, or
        None if no user is found.
    """
    return db.session.get(User, int(id))


class Post(db.Model):
    """
    Represents a post in the application.

    Attributes:
        id (int): The unique identifier for the post.
        body (str): The content of the post.
        timestamp (datetime): The timestamp when the post was created.
        user_id (int): The ID of the user who authored the post.
        author (User): The user who authored the post.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
            index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(
            sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
