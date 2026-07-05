"""Tests for the feed: GET /api/posts.

Arrange data through the repositories, then assert on what a real HTTP
client would see — the JSON contract, not internal details.
"""

from app.db.repositories import like_repo, post_repo, user_repo


def make_user(db, name="alice"):
    return user_repo.create(db, name, "!test-no-password")


def test_empty_feed(client):
    response = client.get("/api/posts")

    assert response.status_code == 200
    assert response.json() == {"items": [], "page": 1, "hasMore": False}


def test_feed_shape_and_order(client, db):
    alice = make_user(db, "alice")
    bob = make_user(db, "bob")
    first = post_repo.create(db, alice["id"], "first post")
    second = post_repo.create(db, bob["id"], "second post")
    like_repo.add(db, alice["id"], second)
    like_repo.add(db, bob["id"], second)
    db.commit()

    body = client.get("/api/posts").json()

    assert [item["body"] for item in body["items"]] == ["second post", "first post"]
    newest = body["items"][0]
    assert newest["author"] == "bob"
    assert newest["likeCount"] == 2
    assert newest["likedByMe"] is False  # nobody is logged in yet
    assert "createdAt" in newest
    assert first != second  # sanity: two distinct posts existed


def test_pagination(client, db):
    alice = make_user(db)
    for i in range(25):
        post_repo.create(db, alice["id"], f"post number {i}")
    db.commit()

    page1 = client.get("/api/posts?page=1").json()
    page3 = client.get("/api/posts?page=3").json()

    assert len(page1["items"]) == 10
    assert page1["hasMore"] is True
    assert len(page3["items"]) == 5
    assert page3["hasMore"] is False


def test_pages_do_not_overlap(client, db):
    alice = make_user(db)
    for i in range(15):
        post_repo.create(db, alice["id"], f"post number {i}")
    db.commit()

    ids_page1 = {item["id"] for item in client.get("/api/posts?page=1").json()["items"]}
    ids_page2 = {item["id"] for item in client.get("/api/posts?page=2").json()["items"]}

    assert ids_page1.isdisjoint(ids_page2)


def test_invalid_page_is_400_with_error_envelope(client):
    response = client.get("/api/posts?page=0")

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION"
    assert error["details"][0]["field"] == "query.page"
