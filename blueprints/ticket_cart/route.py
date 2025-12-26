from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os

from blueprints.model_response import Ok, Error, Result
from database.sql_provider import SQLProvider
from decorators import login_required, role_required
from load_config import load_env_config
from translation import t
from .model_route import (
    CartData,
    model_add_ticket_to_cart,
    model_calculate_cart_data,
    model_clear_cart,
    model_get_sessions_for_cart,
    model_get_available_tickets,
    model_remove_ticket_from_cart,
    model_sell_tickets
)
from cache.redis_cache import RedisCache

ticket_cart_bp = Blueprint('ticket_cart_bp', __name__, template_folder='templates')

db_config = load_env_config("DB_CONFIG")
cache_config = load_env_config("REDIS_CONFIG")

sql_provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
redis_cache = RedisCache(cache_config["redis"])
ttl: float = cache_config.get("ttl", 3600)


@ticket_cart_bp.route('/ticket_cart', methods=['GET'])
@login_required
@role_required
def ticket_cart_get():
    """Отображение сеансов, билетов и корзины"""
    res_sessions: Result[list[dict], str] = model_get_sessions_for_cart(db_config, redis_cache, ttl, sql_provider)
    if isinstance(res_sessions, Error):
        return render_template("error.html", error_message=res_sessions.error)
    selected_session_id = session.get('selected_session_id')
    res_tickets = model_get_available_tickets(db_config, redis_cache, ttl, sql_provider, selected_session_id)
    match res_tickets:
        case Ok():
            tickets = res_tickets.result
        case Error():
            tickets = []
    user_data = session.get("user")
    res_cart: Result[CartData, str] = model_calculate_cart_data(redis_cache, user_data)
    if isinstance(res_cart, Error):
        flash(res_cart.error, category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))
    cart_ids = [ticket["ticket_id"] for ticket in res_cart.result.cart]
    return render_template("ticket_cart.html", 
                            sessions=res_sessions.result, 
                            tickets=tickets,
                            cart=res_cart.result.cart,
                            total_sum=res_cart.result.total,
                            cart_ids=cart_ids)
            


@ticket_cart_bp.route("/select_session", methods=["POST"])
@login_required
@role_required
def select_session():
    """Выбор сеанса для покупки билетов"""
    selected_session_id = request.form.get("selected_session_id")
    
    if selected_session_id:
        session['selected_session_id'] = int(selected_session_id)
        flash(f"🎬 {t('cart.msg.session_picked')}", category="notice")
    else:
        session.pop('selected_session_id', None)
        flash(f"ℹ️ {t('cart.msg.session_reset')}", category="notice")
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/add_ticket/<int:ticket_id>", methods=["POST"])
@login_required
@role_required
def add_ticket_to_cart(ticket_id):
    """Добавление билета в корзину"""
    user_data = session.get("user")
    selected_session_id = session.get("selected_session_id")
    result = model_add_ticket_to_cart(redis_cache, ttl, user_data, ticket_id, selected_session_id)

    match result:
        case Ok():
            flash(result.result, category="ok")
        case Error():
            flash(result.error, category="error")
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))
        

@ticket_cart_bp.route("/remove_ticket/<int:ticket_id>", methods=["POST"])
@login_required
@role_required
def remove_ticket_from_cart(ticket_id):
    """Удаление билета из корзины"""
    user_data = session.get("user")
    res = model_remove_ticket_from_cart(redis_cache, ttl, user_data, ticket_id)
    match res:
        case Ok():
            flash(res.result, category="ok")
        case Error():
            flash(res.error, category="error")
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))
    
@ticket_cart_bp.route("/buy_tickets", methods=["POST"])
@login_required
@role_required
def buy_tickets():
    """Покупка билетов из корзины"""
    user_data = session.get("user")
    res: Result[str, str] = model_sell_tickets(db_config, redis_cache, ttl, sql_provider, user_data)
    match res:
        case Ok():
            flash(res.result, category="ok")
        case Error():
            flash(res.error, category="error")
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/clear_ticket_cart", methods=["POST"])
@login_required
@role_required
def clear_ticket_cart():
    """Очистка корзины"""
    user_data = session.get("user")
    result: Result[str, str] = model_clear_cart(redis_cache, ttl, user_data)
    match result:
        case Ok():
            flash(result.result, category="ok")
        case Error():
            flash(result.error, category="error")
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

