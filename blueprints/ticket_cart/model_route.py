from dataclasses import dataclass
from database.select import select_dict
from cache.redis_cache import RedisCache
from database.DBcm import DBContextManager
from datetime import date, datetime, timedelta
from decimal import Decimal
from database.sql_provider import SQLProvider
from blueprints.model_response import Result, Ok, Error
from translation import get_locale, t


def _serialize_redis_value(val):
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


def model_get_sessions_for_cart(db_config: dict, redis_cache: RedisCache, ttl: float, sql_provider: SQLProvider) -> Result[list[dict], str]:
    """Получить список сеансов для выбора"""
    _sql = sql_provider.get('sessions_for_cart.sql')
    result = select_dict(db_config, _sql, get_locale())
    
    if not result:
        return Error(t("cart.label.no_sessions"))

    for sess in result:
        sess_id = sess["session_id"]
        info_key = f"session:{sess_id}:info"

        info_value = {k: _serialize_redis_value(v) for k, v in {
            "session_id": sess_id,
            "film_title": sess.get("film_title", ""),
            "hall_name": sess.get("hall_name", ""),
            "session_date": sess.get("session_date"),
            "session_time": sess.get("session_time"),
            "display_name": sess.get("display_name", "")
        }.items()}
        redis_cache.set_value(info_key, info_value, ttl)

    return Ok(result)


def model_get_available_tickets(db_config: dict, redis_cache: RedisCache, ttl: float, sql_provider: SQLProvider, session_id) -> Result[list[dict], str]:
    if not session_id:
        return Error(t("cart.label.no_sessions"))
    """Получить список доступных билетов на сеанс"""
    _sql = sql_provider.get('available_tickets.sql')
    result = select_dict(db_config, _sql, (get_locale(), session_id,))
    
    if not result:
        return Error(t("cart.label.no_tickets"))

    for ticket in result:
        ticket_id = ticket["ticket_id"]
        info_key = f"ticket:{ticket_id}:info"

        info_value = {k: _serialize_redis_value(v) for k, v in {
            "ticket_id": ticket_id,
            "session_id": session_id,
            "row_num": ticket.get("row_num", 0),
            "seat_number": ticket.get("seat_number", 0),
            "price": ticket.get("price", 0),
            "film_title": ticket.get("film_title", ""),
            "session_info": ticket.get("session_info", ""),
            "is_sold": ticket.get("is_sold", False)
        }.items()}
        redis_cache.set_value(info_key, info_value, ttl)
    return Ok(result)


@dataclass
class CartData:
    cart: dict
    total: int


def model_calculate_cart_data(redis_cache, user_data) -> Result[CartData, str]:
    if not user_data:
        return Error[str](f"❌ {t('cart.msg.no_user')}")
    user_id = user_data["user_id"]
    cart = redis_cache.get_cart(user_id)
    total_sum = sum(item.get('price', 0) for item in cart)
    return Ok[CartData](CartData(cart, total_sum))


def model_add_ticket_to_cart(redis_cache: RedisCache, ttl: float, user_data, ticket_id, selected_session_id) -> Result[str, str]:
    """Добавление билета в корзину"""
    if not user_data:
        return Error(f"❌ {t('cart.msg.no_user')}")

    user_id = user_data["user_id"]
    cart = redis_cache.get_cart(user_id)

    if not selected_session_id:
        return Error(f"❌ {t('cart.msg.no_session_picked')}")

    info_key = f"ticket:{ticket_id}:info"
    ticket_info = redis_cache.get_value(info_key)
    if not ticket_info:
        return Error(f"❌ {t('cart.msg.no_ticket_info')}")

    for item in cart:
        if item["ticket_id"] == ticket_id:
            return Error(f"⚠️ {t('cart.msg.ticket_already_added')}")

    ticket_item = {
        "ticket_id": ticket_id,
        "session_id": selected_session_id,
        "row_num": ticket_info.get('row_num', 0),
        "seat_number": ticket_info.get('seat_number', 0),
        "price": ticket_info.get('price', 0),
        "film_title": ticket_info.get('film_title', ''),
        "session_info": ticket_info.get('session_info', '')
    }
    
    cart.append(ticket_item)
    redis_cache.set_cart(user_id, cart, ttl)
    return Ok(t("cart.msg.ticket_added_ok", row=ticket_info.get('row_num'), seat_number=ticket_info.get('seat_number')))


def model_remove_ticket_from_cart(redis_cache: RedisCache, ttl: float, user_data, ticket_id) -> Result[str, str]:
    try:
        if not user_data:
            return Error(f"❌ {t('cart.msg.no_user')}")
    
        user_id = user_data["user_id"]
        cart = redis_cache.get_cart(user_id)
        cart = [item for item in cart if item["ticket_id"] != ticket_id]
        redis_cache.set_cart(user_id, cart, ttl)
        return Ok(f"🗑️ {t('cart.msg.ticket_removed')}")
    except Exception as e:
        return Error(f"❌ {t('cart.msg.system_error', cause=str(e))}")


def model_sell_tickets(db_config: dict, redis_cache: RedisCache, ttl: float, sql_provider: SQLProvider, user_data) -> Result[str, str]:
    """Продать билеты (пометить как проданные)"""
    if not user_data:
        return Error(f"❌ {t('cart.msg.no_user')}")
    user_id = user_data["user_id"]
    cart = redis_cache.get_cart(user_id)
    if not cart:
        return Error(f"❌ {t('cart.msg.empty_cart')}")
    ticket_ids = [item["ticket_id"] for item in cart]
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            return Error(t("cart.label.bd_connection_error"))
        try:
            _sql = sql_provider.get('sell_ticket.sql')
            for ticket_id in ticket_ids:
                cursor.execute(_sql, (ticket_id,))
            total_sum = sum(item.get('price', 0) for item in cart)
            ticket_num = len(ticket_ids)
            redis_cache.set_cart(user_id, [], ttl)
            return Ok(t("cart.msg.cart_sold", ticket_num=ticket_num, total_sum=total_sum, currency=t("global.rubles")))
        except Exception as e:
            return Error(f'{t("cart.label.bd_general_error")} {str(e)}')


def model_clear_cart(redis_cache: RedisCache, ttl: float, user_data) -> Result[str, str]:
    if not user_data:
        return Error(f"❌ {t('cart.msg.no_user')}")
    user_id = user_data["user_id"]
    redis_cache.set_cart(user_id, [], ttl)
    return Ok(f"🗑️ {t('cart.msg.cart_cleared')}")

