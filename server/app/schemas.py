"""The API contract, as pydantic models.

These classes define exactly what JSON crosses the wire — nothing more.
Note the aliases: Python names things ``like_count``, JavaScript expects
``likeCount``. The alias marks the seam where one language's conventions
hand over to the other's. FastAPI serializes responses using the aliases
automatically.
"""

from pydantic import BaseModel, Field


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
