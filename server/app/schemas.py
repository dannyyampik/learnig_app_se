"""The API contract, as pydantic models.

These classes define exactly what JSON crosses the wire — nothing more.
Note the aliases: Python names things ``like_count``, JavaScript expects
``likeCount``. The alias marks the seam where one language's conventions
hand over to the other's. FastAPI serializes responses using the aliases
automatically.
"""

from pydantic import BaseModel, Field


class CredentialsIn(BaseModel):
    """What signup and login accept. Declared once, enforced by FastAPI on
    every request — the server-side half of the validation story."""

    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    """What the API says about a user. Note what's absent: password_hash
    stays inside the server, always."""

    id: int
    username: str
    created_at: str = Field(serialization_alias="createdAt")


class PostOut(BaseModel):
    id: int
    body: str
    author: str
    created_at: str = Field(serialization_alias="createdAt")
    like_count: int = Field(serialization_alias="likeCount")
    liked_by_me: bool = Field(serialization_alias="likedByMe")


class FeedPage(BaseModel):
    items: list[PostOut]
    page: int
    has_more: bool = Field(serialization_alias="hasMore")


class PostCreateIn(BaseModel):
    """What creating a post accepts. The same 1–280 rule exists three
    times on purpose: here (reject bad requests), in the DB CHECK
    (last line of defense), and in the composer UI (fast feedback)."""

    body: str = Field(min_length=1, max_length=280)


class ProfileOut(BaseModel):
    """A user's public page: who they are, their numbers, their posts."""

    username: str
    created_at: str = Field(serialization_alias="createdAt")
    post_count: int = Field(serialization_alias="postCount")
    likes_received: int = Field(serialization_alias="likesReceived")
    posts: list[PostOut]
