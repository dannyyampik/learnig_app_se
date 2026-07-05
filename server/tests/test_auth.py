"""Tests for accounts and sessions: /api/auth/*.

TestClient keeps a cookie jar per client, just like a browser — so these
tests exercise the real login mechanics: Set-Cookie on the way out, Cookie
on the way back in.
"""

from app.db.repositories import like_repo, post_repo


def signup(client, username="alice", password="password123"):
    return client.post(
        "/api/auth/signup", json={"username": username, "password": password}
    )


def test_signup_logs_you_in(client):
    response = signup(client)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert "password" not in body and "password_hash" not in body
    assert "sid" in response.cookies  # the session cookie was set

    me = client.get("/api/auth/me").json()
    assert me["username"] == "alice"


def test_duplicate_username_is_409(client):
    signup(client)
    response = signup(client)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_short_password_is_400(client):
    response = signup(client, password="short")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION"


def test_login_roundtrip(client):
    signup(client)
    client.post("/api/auth/logout")

    response = client.post(
        "/api/auth/login", json={"username": "alice", "password": "password123"}
    )

    assert response.status_code == 200
    assert client.get("/api/auth/me").json()["username"] == "alice"


def test_wrong_password_and_unknown_user_look_identical(client):
    signup(client)

    wrong_password = client.post(
        "/api/auth/login", json={"username": "alice", "password": "wrongwrong"}
    )
    unknown_user = client.post(
        "/api/auth/login", json={"username": "nobody99", "password": "wrongwrong"}
    )

    # Same status, same body — no way to probe which usernames exist.
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()


def test_logout_kills_the_session_server_side(client):
    signup(client)
    stolen_cookie = client.cookies["sid"]

    response = client.post("/api/auth/logout")
    assert response.status_code == 204

    # Even presenting the old cookie again gets you nothing: the session
    # row is gone. This is why logout deletes the row, not just the cookie.
    me = client.get("/api/auth/me", cookies={"sid": stolen_cookie})
    assert me.json() is None


def test_logout_requires_being_logged_in(client):
    response = client.post("/api/auth/logout")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_me_is_null_for_strangers(client):
    assert client.get("/api/auth/me").json() is None


def test_feed_knows_what_the_viewer_liked(client, db):
    me = signup(client).json()
    post_id = post_repo.create(db, me["id"], "my own post")
    other = post_repo.create(db, me["id"], "another post")
    like_repo.add(db, me["id"], post_id)
    db.commit()

    items = client.get("/api/posts").json()["items"]
    liked = {item["id"]: item["likedByMe"] for item in items}

    assert liked[post_id] is True
    assert liked[other] is False
