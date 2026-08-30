"""Todo CRUD API -- Flask Blueprint."""
from datetime import datetime

from flask import Blueprint, jsonify, request

from todos.auth import require_auth
from todos.models import Todo
from todos import get_session

todos_bp = Blueprint("todos", __name__, url_prefix="/api/todos")


def _todo_to_dict(todo: Todo) -> dict:
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "priority": todo.priority,
        "created_at": todo.created_at.isoformat() if todo.created_at else None,
        "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
        "user_id": todo.user_id,
    }


@todos_bp.route("", methods=["GET"])
@require_auth
def list_todos(user):
    """List all todos for the current user with pagination and filters."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    completed = request.args.get("completed", type=str)
    priority = request.args.get("priority", type=str)
    search = request.args.get("search", "", type=str)

    session = get_session()
    try:
        query = session.query(Todo).filter(Todo.user_id == user.id)

        if completed is not None:
            flag = completed.lower() in ("true", "1", "yes")
            query = query.filter(Todo.completed == flag)

        if priority is not None:
            try:
                query = query.filter(Todo.priority == int(priority))
            except ValueError:
                return jsonify({"status": "error", "message": "invalid priority value"}), 400

        if search:
            pattern = f"%{search}%"
            query = query.filter(
                Todo.title.ilike(pattern) | Todo.description.ilike(pattern)
            )

        total = query.count()
        todos = query.order_by(Todo.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            "status": "success",
            "data": {
                "todos": [_todo_to_dict(t) for t in todos],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page,
                },
            },
        })
    finally:
        session.close()


@todos_bp.route("/<int:todo_id>", methods=["GET"])
@require_auth
def get_todo(todo_id, user):
    """Get a single todo by ID."""
    session = get_session()
    try:
        todo = session.query(Todo).filter_by(id=todo_id, user_id=user.id).first()
        if not todo:
            return jsonify({"status": "error", "message": "todo not found"}), 404
        return jsonify({"status": "success", "data": _todo_to_dict(todo)})
    finally:
        session.close()


@todos_bp.route("", methods=["POST"])
@require_auth
def create_todo(user):
    """Create a new todo."""
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title or not title.strip():
        return jsonify({"status": "error", "message": "title is required"}), 400

    session = get_session()
    try:
        todo = Todo(
            title=title.strip(),
            description=data.get("description", "").strip() or None,
            priority=int(data.get("priority", 0)),
            completed=False,
            user_id=user.id,
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return jsonify({"status": "success", "data": _todo_to_dict(todo)}), 201
    except Exception:
        session.rollback()
        return jsonify({"status": "error", "message": "internal error"}), 500
    finally:
        session.close()


@todos_bp.route("/<int:todo_id>", methods=["PUT"])
@require_auth
def update_todo(todo_id, user):
    """Update an existing todo."""
    session = get_session()
    try:
        todo = session.query(Todo).filter_by(id=todo_id, user_id=user.id).first()
        if not todo:
            return jsonify({"status": "error", "message": "todo not found"}), 404

        data = request.get_json(silent=True) or {}
        if "title" in data:
            if not data["title"].strip():
                return jsonify({"status": "error", "message": "title cannot be empty"}), 400
            todo.title = data["title"].strip()
        if "description" in data:
            todo.description = data["description"].strip() or None
        if "completed" in data:
            todo.completed = bool(data["completed"])
        if "priority" in data:
            todo.priority = int(data["priority"])
        todo.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(todo)
        return jsonify({"status": "success", "data": _todo_to_dict(todo)})
    except ValueError:
        return jsonify({"status": "error", "message": "invalid priority value"}), 400
    except Exception:
        session.rollback()
        return jsonify({"status": "error", "message": "internal error"}), 500
    finally:
        session.close()


@todos_bp.route("/<int:todo_id>", methods=["DELETE"])
@require_auth
def delete_todo(todo_id, user):
    """Delete a todo."""
    session = get_session()
    try:
        todo = session.query(Todo).filter_by(id=todo_id, user_id=user.id).first()
        if not todo:
            return jsonify({"status": "error", "message": "todo not found"}), 404
        session.delete(todo)
        session.commit()
        return jsonify({"status": "success", "data": {"id": todo_id}})
    except Exception:
        session.rollback()
        return jsonify({"status": "error", "message": "internal error"}), 500
    finally:
        session.close()


@todos_bp.route("/<int:todo_id>/toggle", methods=["PATCH"])
@require_auth
def toggle_todo(todo_id, user):
    """Toggle the completed status of a todo."""
    session = get_session()
    try:
        todo = session.query(Todo).filter_by(id=todo_id, user_id=user.id).first()
        if not todo:
            return jsonify({"status": "error", "message": "todo not found"}), 404
        todo.completed = not todo.completed
        todo.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(todo)
        return jsonify({"status": "success", "data": _todo_to_dict(todo)})
    except Exception:
        session.rollback()
        return jsonify({"status": "error", "message": "internal error"}), 500
    finally:
        session.close()
