from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os

from blueprints.model_response import ModelResponse, ResponseError, ResponseOk
from database.sql_provider import SQLProvider
from decorators import login_required, role_required
from load_config import load_env_config
from translation import t
from .model_route import (
    model_get_sessions_for_cart,
    model_get_available_tickets,
    model_sell_tickets
)
from cache.redis_cache import RedisCache

ticket_cart_bp = Blueprint('ticket_cart_bp', __name__, template_folder='templates')

db_config = load_env_config("DB_CONFIG")
cache_config = load_env_config("REDIS_CONFIG")

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
redis_conn = RedisCache(cache_config["redis"])
TTL = cache_config.get("ttl", 3600)


@ticket_cart_bp.route('/ticket_cart', methods=['GET'])
@login_required
@role_required
def ticket_cart_get():
    """Отображение сеансов, билетов и корзины"""
    res_sessions: ModelResponse = model_get_sessions_for_cart(db_config, provider, cache_config)
    match res_sessions:
        case ResponseOk():
            sessions = res_sessions.result
            
            user_data = session.get("user")
            if not user_data:
                flash(f"❌ {t('cart.msg.no_user')}", category="error")
                return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

            user_id = user_data["user_id"]
            cart = redis_conn.get_cart(user_id)
            
            selected_session_id = session.get('selected_session_id')
            tickets = []
            
            if selected_session_id:
                res_tickets = model_get_available_tickets(db_config, provider, selected_session_id)
                match res_tickets:
                    case ResponseOk():
                        tickets = res_tickets.result
            
            # Считаем общую сумму корзины
            total_sum = sum(item.get('price', 0) for item in cart)
            cart_ids = [ticket["ticket_id"] for ticket in cart]
    
            return render_template("ticket_cart.html", 
                                  sessions=sessions, 
                                  tickets=tickets,
                                  cart=cart,
                                  total_sum=total_sum,
                                  cart_ids=cart_ids)
        case ResponseError():
            return render_template("error.html", error_message=res_sessions.error)


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
    if not user_data:
        flash(f"❌ {t('cart.msg.no_user')}", category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    user_id = user_data["user_id"]
    cart = redis_conn.get_cart(user_id)

    selected_session_id = session.get("selected_session_id")

    if not selected_session_id:
        flash(f"❌ {t('cart.msg.no_session_picked')}", category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    # Получаем информацию о билете из Redis
    info_key = f"ticket:{ticket_id}:info"
    ticket_info = redis_conn.get_value(info_key)
    if not ticket_info:
        flash(f"❌ {t('cart.msg.no_ticket_info')}", category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    # Проверяем, не добавлен ли уже этот билет
    for item in cart:
        if item["ticket_id"] == ticket_id:
            flash(f"⚠️ {t('cart.msg.ticket_already_added')}", category="error")
            return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    # Добавляем в корзину
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
    redis_conn.set_cart(user_id, cart, TTL)
    #flash(f"✅ Билет (ряд {ticket_info.get('row_num')}, место {ticket_info.get('seat_number')}) добавлен", category="ok")
    flash(t("cart.msg.ticket_added_ok", row=ticket_info.get('row_num'), seat_number=ticket_info.get('seat_number')), category="ok")
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/remove_ticket/<int:ticket_id>", methods=["POST"])
@login_required
@role_required
def remove_ticket_from_cart(ticket_id):
    """Удаление билета из корзины"""
    user_data = session.get("user")
    if not user_data:
        flash(f"❌ {t('cart.msg.no_user')}", category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    user_id = user_data["user_id"]
    cart = redis_conn.get_cart(user_id)
    cart = [item for item in cart if item["ticket_id"] != ticket_id]
    redis_conn.set_cart(user_id, cart, TTL)
    flash(f"🗑️ {t('cart.msg.ticket_removed')}", category="notice")
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/buy_tickets", methods=["POST"])
@login_required
@role_required
def buy_tickets():
    """Покупка билетов из корзины"""
    user_data = session.get("user")
    if not user_data:
        flash(f"❌ {t('cart.msg.no_user')}", category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    user_id = user_data["user_id"]
    cart = redis_conn.get_cart(user_id)
    if not cart:
        flash(f"❌ {t('cart.msg.empty_cart')}", category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    ticket_ids = [item["ticket_id"] for item in cart]
    res = model_sell_tickets(db_config, provider, ticket_ids)
    
    match res:
        case ResponseOk():
            total_sum = sum(item.get('price', 0) for item in cart)
            flash(t("cart.msg.cart_sold", ticket_num=len(cart), total_sum=total_sum, currency=t("global.rubles")), category="ok")
            redis_conn.set_cart(user_id, [])
        case ResponseError():
            flash(f"❌ {res.error}", category="error")

    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/clear_ticket_cart", methods=["POST"])
@login_required
@role_required
def clear_ticket_cart():
    """Очистка корзины"""
    user_data = session.get("user")
    if not user_data:
        flash(f"❌ {t('cart.msg.no_user')}", category="error")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    user_id = user_data["user_id"]
    redis_conn.set_cart(user_id, [])
    flash(f"🗑️ {t('cart.msg.cart_cleared')}", category="notice")
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

