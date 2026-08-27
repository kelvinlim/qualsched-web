"""Auth stub: health, Google-unset status, allowlisted dev-login, 401 without cookie."""


def test_health(anon):
    r = anon.get("/health")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.0.1"
    assert body["devLogin"] is True
    assert body["google"] is False


def test_auth_status(anon):
    r = anon.get("/auth/status")
    assert r.status_code == 200
    assert r.json()["devLogin"] is True
    assert r.json()["google"] is False


def test_me_unauthenticated(anon):
    r = anon.get("/auth/me")
    assert r.status_code == 401


def test_config_unauthenticated(anon):
    r = anon.get("/api/config")
    assert r.status_code == 401


def test_dev_login_allowlist(anon):
    r = anon.post("/auth/dev-login", json={"email": "dev@umn.edu"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == "dev@umn.edu"
    assert body["is_superuser"] is True
    assert "qs_session" in r.cookies

    me = anon.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "dev@umn.edu"


def test_dev_login_rejects_unknown(anon):
    r = anon.post("/auth/dev-login", json={"email": "stranger@example.com"})
    assert r.status_code == 403
