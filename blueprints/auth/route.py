from flask import Blueprint, render_template, request, session, redirect, url_for
import os
from database.select import select_dict
from database.sql_provider import SQLProvider
from load_config import load_env_config

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')


def load_role_config():
    return load_env_config("ROLE_CONFIG")


def authenticate_user(login, password):
    current_dir = os.path.dirname(__file__)
    db_config = load_env_config("DB_CONFIG")

    sql_path = os.path.join(current_dir, 'sql')
    provider = SQLProvider(sql_path)

    _sql = provider.get('user_auth.sql')
    users = select_dict(db_config, _sql, (login, password))

    return users[0] if users else None


@auth_bp.route('/login', methods=['GET'])
def login_handler():
    if 'user' in session:
        return redirect(url_for('menu_bp.main_menu'))
    return render_template("login.html")


@auth_bp.route('/login', methods=['POST'])
def login_result_handler():
    login = request.form.get('login')
    password = request.form.get('password')

    user = authenticate_user(login, password)

    if user:
        session['user'] = {
            'user_id': user['user_id'],
            'login': user['login'],
            'role': user['role']
        }
        return redirect(url_for('menu_bp.main_menu'))
    else:
        return render_template("login.html",
                               error_message="Неверный логин или пароль")


@auth_bp.route('/logout')
def logout_handler():
    session.pop('user', None)
    return redirect(url_for('auth_bp.login_handler'))

