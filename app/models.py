from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class User(db.Model):
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

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
            back_populates='author')

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

    def __repr__(self):
        return '<User {}>'.format(self.username)


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
