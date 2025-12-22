from flask import Blueprint, render_template, request, session, redirect, url_for
from database.typing import User
from load_config import load_env_config
from .model_route import model_validate_user

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')


def load_role_config():
    return load_env_config("ROLE_CONFIG")


@auth_bp.route('/login', methods=['GET'])
def login_handler():
    if 'user' in session:
        return redirect(url_for('menu_bp.main_menu'))
    return render_template("login.html")


@auth_bp.route('/login', methods=['POST'])
def login_result_handler():
    login: str | None = request.form.get('login')
    password: str | None = request.form.get('password')

    assert login is not None
    assert password is not None

    user: User | None = model_validate_user(login, password)

    if user:
        session['user'] = {
            'user_id': user.user_id,
            'login': user.login,
            'role': user.role
        }
        return redirect(url_for('menu_bp.main_menu'))
    else:
        return render_template("login.html",
                               error_message="Неверный логин или пароль")


@auth_bp.route('/logout')
def logout_handler():
    session.pop('user', None)
    return redirect(url_for('auth_bp.login_handler'))

