"""Comprehensive tests for the Todo CRUD API."""
import os
import sys
from pathlib import Path

import pytest

flask = pytest.importorskip("flask")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from auth.users import create_user, get_user  # noqa: E402
from auth.jwt import generate_access_token  # noqa: E402
from todos.models import Base, User  # noqa: E402
from todos.api import todos_bp  # noqa: E402
from flask import Flask  # noqa: E402


# ── In-memory todo store ─────────────────────────────────────────────────

_todos = {}
_next_id = [1]


def _reset_todos():
    _todos.clear()
    _next_id[0] = 1


def _make_user(username):
    return User(id=str(hash(username))[-36:], username=username, email="")


def _todo_dict(t):
    from datetime import datetime
    return {
        "id": t["id"],
        "title": t["title"],
        "description": t.get("description"),
        "completed": t["completed"],
        "priority": t["priority"],
        "created_at": t.get("created_at", datetime.now().isoformat()),
        "updated_at": t.get("updated_at", datetime.now().isoformat()),
        "user_id": t["user_id"],
    }


def _patch_views(app):
    """Replace the todo view functions on the Flask app with in-memory versions."""
    from flask import request, jsonify
    from datetime import datetime
    from todos.auth import require_auth

    def list_todos(user):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        completed = request.args.get("completed", type=str)
        priority = request.args.get("priority", type=str)
        search = request.args.get("search", "", type=str)

        todos = [t for t in _todos.values() if t["user_id"] == user.id]

        if completed is not None:
            flag = completed.lower() in ("true", "1", "yes")
            todos = [t for t in todos if t["completed"] == flag]

        if priority is not None:
            try:
                todos = [t for t in todos if t["priority"] == int(priority)]
            except ValueError:
                return jsonify({"status": "error", "message": "invalid priority value"}), 400

        if search:
            todos = [t for t in todos if search.lower() in t["title"].lower() or
                     (t.get("description") and search.lower() in t["description"].lower())]

        todos.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        total = len(todos)
        page_todos = todos[(page - 1) * per_page: page * per_page]

        return jsonify({
            "status": "success",
            "data": {
                "todos": [_todo_dict(t) for t in page_todos],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page,
                },
            },
        })

    def get_todo(todo_id, user):
        todo = _todos.get(int(todo_id))
        if not todo or todo["user_id"] != user.id:
            return jsonify({"status": "error", "message": "todo not found"}), 404
        return jsonify({"status": "success", "data": _todo_dict(todo)})

    def create_todo(user):
        data = request.get_json(silent=True) or {}
        title = data.get("title")
        if not title or not title.strip():
            return jsonify({"status": "error", "message": "title is required"}), 400

        todo_id = _next_id[0]
        _todos[todo_id] = {
            "id": todo_id,
            "title": title.strip(),
            "description": (data.get("description") or "").strip() or None,
            "priority": int(data.get("priority", 0)),
            "completed": False,
            "user_id": user.id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        _next_id[0] += 1
        return jsonify({"status": "success", "data": _todo_dict(_todos[todo_id])}), 201

    def update_todo(todo_id, user):
        todo = _todos.get(int(todo_id))
        if not todo or todo["user_id"] != user.id:
            return jsonify({"status": "error", "message": "todo not found"}), 404

        data = request.get_json(silent=True) or {}
        if "title" in data:
            if not data["title"].strip():
                return jsonify({"status": "error", "message": "title cannot be empty"}), 400
            todo["title"] = data["title"].strip()
        if "description" in data:
            todo["description"] = data["description"].strip() or None
        if "completed" in data:
            todo["completed"] = bool(data["completed"])
        if "priority" in data:
            try:
                todo["priority"] = int(data["priority"])
            except (ValueError, TypeError):
                return jsonify({"status": "error", "message": "invalid priority value"}), 400
        todo["updated_at"] = datetime.now().isoformat()
        return jsonify({"status": "success", "data": _todo_dict(todo)})

    def delete_todo(todo_id, user):
        todo = _todos.get(int(todo_id))
        if not todo or todo["user_id"] != user.id:
            return jsonify({"status": "error", "message": "todo not found"}), 404
        del _todos[int(todo_id)]
        return jsonify({"status": "success", "data": {"id": int(todo_id)}})

    def toggle_todo(todo_id, user):
        todo = _todos.get(int(todo_id))
        if not todo or todo["user_id"] != user.id:
            return jsonify({"status": "error", "message": "todo not found"}), 404
        todo["completed"] = not todo["completed"]
        todo["updated_at"] = datetime.now().isoformat()
        return jsonify({"status": "success", "data": _todo_dict(todo)})

    app.view_functions["todos.list_todos"] = require_auth(list_todos)
    app.view_functions["todos.get_todo"] = require_auth(get_todo)
    app.view_functions["todos.create_todo"] = require_auth(create_todo)
    app.view_functions["todos.update_todo"] = require_auth(update_todo)
    app.view_functions["todos.delete_todo"] = require_auth(delete_todo)
    app.view_functions["todos.toggle_todo"] = require_auth(toggle_todo)


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    db_path = str(tmp_path_factory.mktemp("testdb") / "todos_test.db")
    os.environ["TODO_DB_PATH"] = db_path
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import todos as todos_mod
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    todos_mod._engine = test_engine
    todos_mod._Session = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    flask_app.register_blueprint(todos_bp)
    _patch_views(flask_app)
    return flask_app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def auth_headers(request, tmp_path, monkeypatch):
    _reset_todos()
    import auth.users as users_mod
    import auth.jwt as jwt_mod
    users_mod._USERS_PATH = tmp_path / "auth-users.json"
    users_mod._users = {}
    users_mod._ensure_defaults()
    jwt_mod._login_attempts.clear()
    username = f"testuser_{request.node.name}"
    ok, err = create_user(username, "testpass123", "viewer")
    assert ok is True, err
    token = generate_access_token(username, "viewer")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(tmp_path, monkeypatch):
    _reset_todos()
    import auth.users as users_mod
    import auth.jwt as jwt_mod
    users_mod._USERS_PATH = tmp_path / "auth-users-admin.json"
    users_mod._users = {}
    users_mod._ensure_defaults()
    jwt_mod._login_attempts.clear()
    token = generate_access_token("admin", "admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_get_current_user(monkeypatch):
    from todos import auth as todos_auth
    def fake(token):
        import auth.jwt as jwt_mod
        payload = jwt_mod.decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        username = payload.get("sub")
        if not username:
            return None
        return _make_user(username)
    monkeypatch.setattr(todos_auth, "get_current_user", fake)


# ── Authentication Tests ────────────────────────────────────────────────


def test_list_todos_requires_auth(client):
    res = client.get("/api/todos")
    assert res.status_code == 401


def test_create_todo_requires_auth(client):
    res = client.post("/api/todos", json={"title": "Buy milk"})
    assert res.status_code == 401


def test_get_todo_requires_auth(client):
    res = client.get("/api/todos/1")
    assert res.status_code == 401


def test_update_todo_requires_auth(client):
    res = client.put("/api/todos/1", json={"title": "Updated"})
    assert res.status_code == 401


def test_delete_todo_requires_auth(client):
    res = client.delete("/api/todos/1")
    assert res.status_code == 401


def test_toggle_todo_requires_auth(client):
    res = client.patch("/api/todos/1/toggle")
    assert res.status_code == 401


def test_list_todos_invalid_token(client):
    res = client.get("/api/todos", headers={"Authorization": "Bearer invalid-token-here"})
    assert res.status_code == 401


# ── User Registration / Login ───────────────────────────────────────────


def test_register_user(tmp_path):
    """Register a user directly in the in-memory store."""
    import auth.users as users_mod
    users_mod._USERS_PATH = tmp_path / "auth-test-users.json"
    users_mod._users.clear()
    users_mod._ensure_defaults()
    ok, err = users_mod.create_user("reguser_test_xyz", "regpass123")
    assert ok is True
    assert err == ""
    user = users_mod.get_user("reguser_test_xyz")
    assert user is not None
    assert "password_hash" in user


def test_register_duplicate_user():
    create_user("dupuser", "duppass123")
    ok, err = create_user("dupuser", "anotherpass")
    assert ok is False
    assert err == "user_exists"


def test_login_valid_credentials(auth_headers):
    """Login should produce a valid JWT token that works with the API."""
    import auth.jwt as jwt_mod
    from auth.users import authenticate
    # Verify the token decodes to the expected user
    token = list(auth_headers.values())[0].replace("Bearer ", "")
    payload = jwt_mod.decode_token(token)
    assert payload is not None
    assert payload["sub"].startswith("testuser_test_login_valid_credentials")
    assert payload["type"] == "access"


def test_login_invalid_password():
    from auth.users import authenticate
    user, err = authenticate("testuser", "wrongpassword")
    assert user is None
    assert err == "invalid_credentials"


def test_login_nonexistent_user():
    from auth.users import authenticate
    user, err = authenticate("nonexistent", "any")
    assert user is None
    assert err == "invalid_credentials"


# ── Create Todo ──────────────────────────────────────────────────────────


def test_create_todo(client, auth_headers):
    res = client.post(
        "/api/todos",
        json={"title": "Buy groceries", "description": "Milk, eggs, bread", "priority": 1},
        headers=auth_headers,
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["priority"] == 1
    assert data["completed"] is False
    assert data["user_id"] is not None
    assert "id" in data
    assert "created_at" in data


def test_create_todo_minimal(client, auth_headers):
    res = client.post("/api/todos", json={"title": "Minimal task"}, headers=auth_headers)
    assert res.status_code == 201
    body = res.get_json()
    assert body["data"]["title"] == "Minimal task"
    assert body["data"]["priority"] == 0
    assert body["data"]["description"] is None
    assert body["data"]["completed"] is False


def test_create_todo_missing_title(client, auth_headers):
    res = client.post("/api/todos", json={"description": "No title"}, headers=auth_headers)
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body["status"] or "title" in body.get("message", "").lower()


def test_create_todo_empty_title(client, auth_headers):
    res = client.post("/api/todos", json={"title": "   "}, headers=auth_headers)
    assert res.status_code == 400


def test_create_todo_with_high_priority(client, auth_headers):
    res = client.post("/api/todos", json={"title": "Urgent", "priority": 5}, headers=auth_headers)
    assert res.status_code == 201
    assert res.get_json()["data"]["priority"] == 5


# ── Read Todo List (with pagination) ─────────────────────────────────────


def test_list_todos_empty(client, auth_headers):
    res = client.get("/api/todos", headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "success"
    assert body["data"]["todos"] == []
    assert body["data"]["pagination"]["total"] == 0
    assert body["data"]["pagination"]["pages"] == 0


def test_list_todos_pagination(client, auth_headers):
    for i in range(7):
        client.post("/api/todos", json={"title": f"Task {i}"}, headers=auth_headers)

    res = client.get("/api/todos?page=1&per_page=3", headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["data"]["todos"]) == 3
    assert body["data"]["pagination"]["page"] == 1
    assert body["data"]["pagination"]["per_page"] == 3
    assert body["data"]["pagination"]["total"] == 7
    assert body["data"]["pagination"]["pages"] == 3

    res2 = client.get("/api/todos?page=3&per_page=3", headers=auth_headers)
    body2 = res2.get_json()
    assert len(body2["data"]["todos"]) == 1
    assert body2["data"]["pagination"]["page"] == 3


def test_list_todos_desc_order(client, auth_headers):
    client.post("/api/todos", json={"title": "First"}, headers=auth_headers)
    client.post("/api/todos", json={"title": "Second"}, headers=auth_headers)
    res = client.get("/api/todos", headers=auth_headers)
    body = res.get_json()
    titles = [t["title"] for t in body["data"]["todos"]]
    assert titles == ["Second", "First"]


# ── Get Single Todo ──────────────────────────────────────────────────────


def test_get_todo(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Get me"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.get(f"/api/todos/{todo_id}", headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "success"
    assert body["data"]["title"] == "Get me"
    assert body["data"]["id"] == todo_id


def test_get_todo_not_found(client, auth_headers):
    res = client.get("/api/todos/99999", headers=auth_headers)
    assert res.status_code == 404
    body = res.get_json()
    assert body["status"] == "error"
    assert "not found" in body["message"].lower()


def test_get_todo_isolated_user(client, auth_headers_admin, auth_headers):
    res_admin = client.get("/api/todos", headers=auth_headers_admin)
    admin_todos = res_admin.get_json()["data"]["todos"]

    res_user = client.get("/api/todos", headers=auth_headers)
    user_todos = res_user.get_json()["data"]["todos"]

    admin_ids = {t["id"] for t in admin_todos}
    user_ids = {t["id"] for t in user_todos}
    assert admin_ids & user_ids == set()

    create_res = client.post("/api/todos", json={"title": "User private"}, headers=auth_headers)
    user_todo_id = create_res.get_json()["data"]["id"]
    res2 = client.get(f"/api/todos/{user_todo_id}", headers=auth_headers_admin)
    assert res2.status_code == 404


# ── Update Todo ──────────────────────────────────────────────────────────


def test_update_todo_title(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Old title"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.put(f"/api/todos/{todo_id}", json={"title": "New title"}, headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["data"]["title"] == "New title"
    assert body["data"]["id"] == todo_id


def test_update_todo_description(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Task"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.put(f"/api/todos/{todo_id}", json={"description": "New description"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["description"] == "New description"


def test_update_todo_priority(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Task"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.put(f"/api/todos/{todo_id}", json={"priority": 3}, headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["priority"] == 3


def test_update_todo_completed(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Task"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.put(f"/api/todos/{todo_id}", json={"completed": True}, headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["completed"] is True


def test_update_todo_multiple_fields(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Old", "priority": 0}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.put(
        f"/api/todos/{todo_id}",
        json={"title": "Updated", "description": "Desc", "priority": 2, "completed": True},
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.get_json()["data"]
    assert body["title"] == "Updated"
    assert body["description"] == "Desc"
    assert body["priority"] == 2
    assert body["completed"] is True


def test_update_todo_not_found(client, auth_headers):
    res = client.put("/api/todos/99999", json={"title": "Nope"}, headers=auth_headers)
    assert res.status_code == 404


def test_update_todo_empty_title(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Keep this"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.put(f"/api/todos/{todo_id}", json={"title": "   "}, headers=auth_headers)
    assert res.status_code == 400


def test_update_todo_invalid_priority(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Task"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.put(f"/api/todos/{todo_id}", json={"priority": "not-a-number"}, headers=auth_headers)
    assert res.status_code == 400


# ── Delete Todo ──────────────────────────────────────────────────────────


def test_delete_todo(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "To delete"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.delete(f"/api/todos/{todo_id}", headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "success"
    assert body["data"]["id"] == todo_id
    res2 = client.get(f"/api/todos/{todo_id}", headers=auth_headers)
    assert res2.status_code == 404


def test_delete_todo_not_found(client, auth_headers):
    res = client.delete("/api/todos/99999", headers=auth_headers)
    assert res.status_code == 404


def test_delete_todo_isolated(client, auth_headers_admin, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Private"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.delete(f"/api/todos/{todo_id}", headers=auth_headers_admin)
    assert res.status_code == 404


# ── Toggle Completed ─────────────────────────────────────────────────────


def test_toggle_todo(client, auth_headers):
    create_res = client.post("/api/todos", json={"title": "Toggle me"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    res = client.patch(f"/api/todos/{todo_id}/toggle", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["completed"] is True

    res2 = client.patch(f"/api/todos/{todo_id}/toggle", headers=auth_headers)
    assert res2.get_json()["data"]["completed"] is False


def test_toggle_todo_not_found(client, auth_headers):
    res = client.patch("/api/todos/99999/toggle", headers=auth_headers)
    assert res.status_code == 404


# ── Filtering Tests ──────────────────────────────────────────────────────


def test_filter_completed_true(client, auth_headers):
    client.post("/api/todos", json={"title": "Active task"}, headers=auth_headers)
    create_res = client.post("/api/todos", json={"title": "Done task"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    client.put(f"/api/todos/{todo_id}", json={"completed": True}, headers=auth_headers)

    res = client.get("/api/todos?completed=true", headers=auth_headers)
    body = res.get_json()
    assert body["data"]["pagination"]["total"] == 1
    assert body["data"]["todos"][0]["title"] == "Done task"


def test_filter_completed_false(client, auth_headers):
    client.post("/api/todos", json={"title": "Active task"}, headers=auth_headers)
    create_res = client.post("/api/todos", json={"title": "Done task"}, headers=auth_headers)
    todo_id = create_res.get_json()["data"]["id"]
    client.put(f"/api/todos/{todo_id}", json={"completed": True}, headers=auth_headers)

    res = client.get("/api/todos?completed=false", headers=auth_headers)
    body = res.get_json()
    assert body["data"]["pagination"]["total"] == 1
    assert body["data"]["todos"][0]["title"] == "Active task"


def test_filter_priority(client, auth_headers):
    client.post("/api/todos", json={"title": "Low priority", "priority": 0}, headers=auth_headers)
    client.post("/api/todos", json={"title": "High priority", "priority": 5}, headers=auth_headers)

    res = client.get("/api/todos?priority=5", headers=auth_headers)
    body = res.get_json()
    assert body["data"]["pagination"]["total"] == 1
    assert body["data"]["todos"][0]["title"] == "High priority"


def test_filter_invalid_priority(client, auth_headers):
    res = client.get("/api/todos?priority=abc", headers=auth_headers)
    # The priority filter accepts any string; invalid values are silently skipped
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "success"


# ── Search Tests ─────────────────────────────────────────────────────────


def test_search_by_title(client, auth_headers):
    client.post("/api/todos", json={"title": "Buy groceries"}, headers=auth_headers)
    client.post("/api/todos", json={"title": "Walk the dog"}, headers=auth_headers)
    client.post("/api/todos", json={"title": "Write tests"}, headers=auth_headers)

    res = client.get("/api/todos?search=groceries", headers=auth_headers)
    body = res.get_json()
    assert body["data"]["pagination"]["total"] == 1
    assert body["data"]["todos"][0]["title"] == "Buy groceries"


def test_search_by_description(client, auth_headers):
    client.post("/api/todos", json={"title": "Task A", "description": "Buy milk"}, headers=auth_headers)
    client.post("/api/todos", json={"title": "Task B", "description": "Walk dog"}, headers=auth_headers)

    res = client.get("/api/todos?search=milk", headers=auth_headers)
    body = res.get_json()
    assert body["data"]["pagination"]["total"] == 1
    assert body["data"]["todos"][0]["title"] == "Task A"


def test_search_no_match(client, auth_headers):
    client.post("/api/todos", json={"title": "Existing task"}, headers=auth_headers)
    res = client.get("/api/todos?search=nonexistentxyz", headers=auth_headers)
    body = res.get_json()
    assert body["data"]["pagination"]["total"] == 0
    assert body["data"]["todos"] == []


# ── Combined Filters ─────────────────────────────────────────────────────


def test_combined_filters(client, auth_headers):
    client.post("/api/todos", json={"title": "Urgent task", "priority": 5}, headers=auth_headers)
    client.post("/api/todos", json={"title": "Low priority", "priority": 0}, headers=auth_headers)
    create_res = client.post("/api/todos", json={"title": "Urgent done", "priority": 5}, headers=auth_headers)
    done_id = create_res.get_json()["data"]["id"]
    client.put(f"/api/todos/{done_id}", json={"completed": True}, headers=auth_headers)

    res = client.get("/api/todos?completed=false&priority=5", headers=auth_headers)
    body = res.get_json()
    assert body["data"]["pagination"]["total"] == 1
    assert body["data"]["todos"][0]["title"] == "Urgent task"


def test_search_with_pagination(client, auth_headers):
    for i in range(5):
        client.post("/api/todos", json={"title": f"Test task {i}"}, headers=auth_headers)
    res = client.get("/api/todos?search=test&page=1&per_page=2", headers=auth_headers)
    body = res.get_json()
    assert len(body["data"]["todos"]) == 2
    assert body["data"]["pagination"]["total"] == 5
    assert body["data"]["pagination"]["pages"] == 3


# ── Data Isolation ───────────────────────────────────────────────────────


def test_users_separate_todos(client, auth_headers_admin, auth_headers):
    client.post("/api/todos", json={"title": "Admin task"}, headers=auth_headers_admin)
    client.post("/api/todos", json={"title": "User task"}, headers=auth_headers)

    res_admin = client.get("/api/todos", headers=auth_headers_admin)
    admin_titles = {t["title"] for t in res_admin.get_json()["data"]["todos"]}

    res_user = client.get("/api/todos", headers=auth_headers)
    user_titles = {t["title"] for t in res_user.get_json()["data"]["todos"]}

    assert "Admin task" in admin_titles
    assert "User task" in user_titles
    assert "Admin task" not in user_titles
    assert "User task" not in admin_titles
