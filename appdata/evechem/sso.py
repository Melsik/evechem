from flask.ext.login import LoginManager, login_required, current_user, login_user,


login_manager = LoginManager()

@login_manager.user_loader
def load_user(session_token):
    return User.query.filter_by(session_token=session_token).first()