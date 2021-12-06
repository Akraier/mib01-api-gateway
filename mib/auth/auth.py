import functools

from flask_login import LoginManager, current_user

from mib.rao.user_manager import UserManager 
from mib.auth.user import User

login_manager = LoginManager()


def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return login_manager.unauthorized()
        return func(*args, **kw)
    return _admin_required


@login_manager.user_loader
def load_user(user_id):
    user = UserManager.get_user_by_id(user_id)
    if user is not None:
        user.authenticated = True
    return user