from dataclasses import dataclass

from blueprints.model_response import Error, Ok, Result
from translation import get_locale, t
from database.select import select_dict, select_typed 
from database.sql_provider import SQLProvider
from load_config import load_env_config
import os


@dataclass
class SessionBrief:
    session_id: int
    display_name: str


def model_get_sessions() -> Result[list[SessionBrief], str]:
    """Получить список доступных сеансов"""
    db_config = load_env_config("DB_CONFIG")
    sql_provider: SQLProvider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    try:
        _sql = sql_provider.get('get_sessions.sql')
        params = (get_locale())
        result = select_typed(SessionBrief, db_config, _sql, params)
        return Ok(result)
    except Exception as e:
        return Error(t("seats.label.system_error", cause=str(e)))


def model_available_seats(session_id) -> Result[list[dict], str]:
    """Получить свободные места на сеанс"""
    db_config = load_env_config("DB_CONFIG")
    sql_provider: SQLProvider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    try:
        _sql = sql_provider.get('available_seats.sql')
        result = select_dict(db_config, _sql, session_id)
        if result:
            return Ok([{
                **tb,
                "price": f'{tb["price"]} {t("global.rubles")}',
                "is_sold": t(f'seats.label.is_sold.{tb["is_sold"]}')
            } for tb in result])
        return Error(t("seats.label.no_seats"))
    except Exception as e:
        return Error(str(e))

