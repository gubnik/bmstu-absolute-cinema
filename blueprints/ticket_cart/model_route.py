from database.select import select_dict
from cache.redis_cache import RedisCache
from database.DBcm import DBContextManager
from datetime import date, datetime, timedelta
from decimal import Decimal
from load_config import load_env_config
from blueprints.model_response import ModelResponse, ResponseOk, ResponseError
from translation import t


def serialize_value(val):
    """Сериализация значений для Redis"""
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    elif isinstance(val, timedelta):
        total_seconds = int(val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    elif isinstance(val, Decimal):
        return float(val)
    return val


def model_get_sessions_for_cart(db_config, sql_provider, cache_config) -> ModelResponse:
    """Получить список сеансов для выбора"""
    _sql = sql_provider.get('sessions_for_cart.sql')
    result = select_dict(db_config, _sql)
    
    if not result:
        return ResponseError(t("cart.label.no_sessions"))

    redis_conn = RedisCache(cache_config["redis"])
    ttl = cache_config.get("ttl", 3600)

    for sess in result:
        sess_id = sess["session_id"]
        info_key = f"session:{sess_id}:info"

        info_value = {k: serialize_value(v) for k, v in {
            "session_id": sess_id,
            "film_title": sess.get("film_title", ""),
            "hall_name": sess.get("hall_name", ""),
            "session_date": sess.get("session_date"),
            "session_time": sess.get("session_time"),
            "display_name": sess.get("display_name", "")
        }.items()}
        redis_conn.set_value(info_key, info_value, ttl)

    return ResponseOk(result)


def model_get_available_tickets(db_config, sql_provider, session_id) -> ModelResponse:
    """Получить список доступных билетов на сеанс"""
    _sql = sql_provider.get('available_tickets.sql')
    result = select_dict(db_config, _sql, (session_id,))
    
    if not result:
        return ResponseError(t("cart.label.no_tickets"))

    # Сохраняем информацию о билетах в Redis
    cache_config = load_env_config("REDIS_CONFIG")
    redis_conn = RedisCache(cache_config["redis"])
    ttl = cache_config.get("ttl", 3600)
    for ticket in result:
        ticket_id = ticket["ticket_id"]
        info_key = f"ticket:{ticket_id}:info"

        info_value = {k: serialize_value(v) for k, v in {
            "ticket_id": ticket_id,
            "session_id": session_id,
            "row_num": ticket.get("row_num", 0),
            "seat_number": ticket.get("seat_number", 0),
            "price": ticket.get("price", 0),
            "film_title": ticket.get("film_title", ""),
            "session_info": ticket.get("session_info", ""),
            "is_sold": ticket.get("is_sold", False)
        }.items()}
        redis_conn.set_value(info_key, info_value, ttl)
    return ResponseOk(result)


def model_sell_tickets(db_config, sql_provider, ticket_ids) -> ModelResponse:
    """Продать билеты (пометить как проданные)"""
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            return ResponseError(t("cart.label.bd_connection_error")) #"Ошибка подключения к БД")
        try:
            _sql = sql_provider.get('sell_ticket.sql')
            for ticket_id in ticket_ids:
                cursor.execute(_sql, (ticket_id,))
            return ResponseOk([{'sold_count': len(ticket_ids)}])
        except Exception as e:
            return ResponseError(f'{t("cart.label.bd_general_error")} {str(e)}')

