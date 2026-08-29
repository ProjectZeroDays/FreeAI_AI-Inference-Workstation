"""FreeAI authentication package: JWT tokens and user management."""

from auth.jwt import jwt_auth, JWTAuth  # noqa: F401
from auth.users import (  # noqa: F401
    reload as reload_users,
    get_user,
    authenticate,
    create_user,
    change_password,
    set_role,
    list_users,
    delete_user,
    require_role,
)
from auth.rbac import (  # noqa: F401
    login_required,
    require_role as require_role_decorator,
    get_permission_map,
    apply_rbac_middleware,
    resolve_route_permission,
)
