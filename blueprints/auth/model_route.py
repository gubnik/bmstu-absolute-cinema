from load_config import load_env_config
import os
from database.select import select_typed
from database.sql_provider import SQLProvider
from database.typing import User

def model_validate_user(login: str, password: str):
    db_config = load_env_config("ROLE_CONFIG")
    db_config = load_env_config("DB_CONFIG")
    current_dir = os.path.dirname(__file__)

    sql_path = os.path.join(current_dir, 'sql')
    provider = SQLProvider(sql_path)

    _sql = provider.get('user_auth.sql')
    users: list[User] = select_typed(User, db_config, _sql, (login, password))

    # it is impossible to get more than one user since login is unique
    return users[0] if users else None

