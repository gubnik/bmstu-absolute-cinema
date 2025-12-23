from dataclasses import asdict, dataclass
from typing import cast

from translation.translator import t
from database.select import select_typed 
from database.sql_provider import SQLProvider
from load_config import load_env_config
import os

@dataclass
class SessionBrief:
    session_id: int
    display_name: str


@dataclass
class TicketBrief:
    ticket_id: int
    row_num: int
    seat_number: int
    price: str
    is_sold: str


@dataclass
class SeatsInfoResponse:
    result: list[dict] | None
    error_message: str


def model_get_sessions() -> list[SessionBrief] | None:
    """Получить список доступных сеансов"""
    db_config = load_env_config("DB_CONFIG")
    sql_provider: SQLProvider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    try:
        _sql = sql_provider.get('get_sessions.sql')
        result: list[SessionBrief] = select_typed(SessionBrief, db_config, _sql)
        return result
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return None


def model_available_seats(session_id):
    """Получить свободные места на сеанс"""
    db_config = load_env_config("DB_CONFIG")
    sql_provider: SQLProvider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    try:
        _sql = sql_provider.get('available_seats.sql')
        result: list[TicketBrief] = select_typed(TicketBrief, db_config, _sql, session_id)
        if result:
            rubles_str = t("global.rubles")
            return SeatsInfoResponse([{
                "ticket_id": tb.ticket_id,
                "row_num": tb.row_num,
                "seat_number": tb.seat_number,
                "price": f"{tb.price} {rubles_str}",
                "is_sold": t(f"seats.label.is_sold.{tb.is_sold}")
            } for tb in result], '')
        return SeatsInfoResponse(None, 'Свободные места не найдены или билеты ещё не сгенерированы')
    except Exception as e:
        return SeatsInfoResponse(None, str(e))

