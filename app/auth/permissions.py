"""SRS Sections 2.3, 4.6, and 5.5: capability checks also apply to crafted requests."""
from functools import wraps

from flask import abort
from flask_login import current_user, login_required

CAPABILITIES = {
    "view_admin": {1, 2, 3},
    "add_paint": {1, 2, 3},
    "update_paint": {2, 3},
    "delete_paint": {3},
    "create_admin_level_1": {1, 2, 3},
    "create_admin_level_2": {2, 3},
    "create_admin_level_3": {3},
}


def can(capability):
    return current_user.is_authenticated and current_user.level in CAPABILITIES.get(capability, set())


def require_capability(capability):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not can(capability):
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
