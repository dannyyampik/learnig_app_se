"""Tests for writing: creating/deleting posts, liking, and profiles.

The REST semantics under test are the ones the design calls out:
201 for created, 401 vs 403 vs 404 meaning different refusals, and
PUT/DELETE likes being idempotent.
"""


def signup(client, username="alice"):
    return client.post(
        "/api/auth/signup", json={"username": username, "password": "password123"}
    ).json()


def create_post(client, body="hello world"):
    return client.post("/api/posts", json={"body": body})


def test_create_post_appears_in_feed(client):
    signup(client)

    response = create_post(client, "my first post")

    assert response.status_code == 201
    post = response.json()
    assert post["body"] == "my first post"
    assert post["author"] == "alice"
    assert post["likeCount"] == 0

    feed = client.get("/api/posts").json()
    assert feed["items"][0]["id"] == post["id"]


def test_create_post_requires_login(client):
    response = create_post(client)

    assert response.status_code == 401


def test_create_post_validates_length(client):
    signup(client)

    too_long = create_post(client, "x" * 281)
    empty = create_post(client, "")

    assert too_long.status_code == 400
    assert empty.status_code == 400


def test_delete_own_post(client):
    signup(client)
    post_id = create_post(client).json()["id"]

    response = client.delete(f"/api/posts/{post_id}")

    assert response.status_code == 204
    assert client.get("/api/posts").json()["items"] == []


def test_cannot_delete_someone_elses_post(client):
    signup(client, "alice")
    post_id = create_post(client, "alice's post").json()["id"]
    client.post("/api/auth/logout")
    signup(client, "bob")

    response = client.delete(f"/api/posts/{post_id}")

    # 403, not 404: the post exists, bob just isn't allowed.
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_delete_missing_post_is_404(client):
    signup(client)

    response = client.delete("/api/posts/9999")

    assert response.status_code == 404


def test_like_is_idempotent(client):
    signup(client)
    post_id = create_post(client).json()["id"]

    first = client.put(f"/api/posts/{post_id}/like")
    second = client.put(f"/api/posts/{post_id}/like")  # retry — e.g. flaky network

    assert first.status_code == second.status_code == 204
    post = client.get("/api/posts").json()["items"][0]
    assert post["likeCount"] == 1  # not 2 — that's the whole point of PUT
    assert post["likedByMe"] is True


def test_unlike_is_idempotent(client):
    signup(client)
    post_id = create_post(client).json()["id"]
    client.put(f"/api/posts/{post_id}/like")

    client.delete(f"/api/posts/{post_id}/like")
    response = client.delete(f"/api/posts/{post_id}/like")

    assert response.status_code == 204
    assert client.get("/api/posts").json()["items"][0]["likeCount"] == 0


def test_like_missing_post_is_404(client):
    signup(client)

    response = client.put("/api/posts/9999/like")

    assert response.status_code == 404


def test_profile_shows_stats_and_posts(client):
    signup(client, "alice")
    first = create_post(client, "post one").json()["id"]
    create_post(client, "post two")
    client.post("/api/auth/logout")
    signup(client, "bob")
    client.put(f"/api/posts/{first}/like")

    profile = client.get("/api/users/alice").json()

    assert profile["username"] == "alice"
    assert profile["postCount"] == 2
    assert profile["likesReceived"] == 1
    assert [p["body"] for p in profile["posts"]] == ["post two", "post one"]


def test_unknown_profile_is_404(client):
    response = client.get("/api/users/nobody99")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
