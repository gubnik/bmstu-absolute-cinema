from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
from database.sql_provider import SQLProvider
from decorators import login_required, role_required
from load_config import load_env_config
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
    try:
        res_sessions = model_get_sessions_for_cart(db_config, provider, cache_config)
        
        if not res_sessions.status:
            return render_template("error.html", error_message=res_sessions.error_message)
        
        sessions = res_sessions.result
        
        # Получаем корзину билетов
        user_data = session.get("user")
        user_id = user_data["user_id"]
        cart = redis_conn.get_cart(user_id)
        
        # Получаем выбранный сеанс и его билеты
        selected_session_id = session.get('selected_session_id')
        tickets = []
        
        if selected_session_id:
            res_tickets = model_get_available_tickets(db_config, provider, selected_session_id)
            if res_tickets.status:
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
        
    except Exception as e:
        return render_template("error.html", error_message=f"Системная ошибка: {str(e)}")


@ticket_cart_bp.route("/select_session", methods=["POST"])
@login_required
@role_required
def select_session():
    """Выбор сеанса для покупки билетов"""
    selected_session_id = request.form.get("selected_session_id")
    
    if selected_session_id:
        session['selected_session_id'] = int(selected_session_id)
        flash("🎬 Сеанс выбран")
    else:
        session.pop('selected_session_id', None)
        flash("ℹ️ Выбор сеанса сброшен")
    
    """
    # Очищаем корзину при смене сеанса
    user_data = session.get("user")
    if user_data:
        user_id = user_data["user_id"]
        redis_conn.set_cart(user_id, [])
    """
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/add_ticket/<int:ticket_id>", methods=["POST"])
@login_required
@role_required
def add_ticket_to_cart(ticket_id):
    """Добавление билета в корзину"""
    user_data = session.get("user")
    user_id = user_data["user_id"]
    cart = redis_conn.get_cart(user_id)

    selected_session_id = session.get("selected_session_id")

    if not selected_session_id:
        flash("❌ Сначала выберите сеанс")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    # Получаем информацию о билете из Redis
    info_key = f"ticket:{ticket_id}:info"
    ticket_info = redis_conn.get_value(info_key)
    if not ticket_info:
        flash("❌ Информация о билете не найдена")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    # Проверяем, не добавлен ли уже этот билет
    for item in cart:
        if item["ticket_id"] == ticket_id:
            flash("⚠️ Этот билет уже в корзине")
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
    flash(f"✅ Билет (ряд {ticket_info.get('row_num')}, место {ticket_info.get('seat_number')}) добавлен")
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/remove_ticket/<int:ticket_id>", methods=["POST"])
@login_required
@role_required
def remove_ticket_from_cart(ticket_id):
    """Удаление билета из корзины"""
    user_data = session.get("user")
    user_id = user_data["user_id"]
    cart = redis_conn.get_cart(user_id)

    cart = [item for item in cart if item["ticket_id"] != ticket_id]
    redis_conn.set_cart(user_id, cart, TTL)
    flash("🗑️ Билет удалён из корзины")
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/buy_tickets", methods=["POST"])
@login_required
@role_required
def buy_tickets():
    """Покупка билетов из корзины"""
    user_data = session.get("user")
    user_id = user_data["user_id"]

    cart = redis_conn.get_cart(user_id)
    if not cart:
        flash("❌ Корзина пуста")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    # Получаем список ID билетов
    ticket_ids = [item["ticket_id"] for item in cart]
    
    # Продаём билеты
    res = model_sell_tickets(db_config, provider, ticket_ids)
    
    if res.status:
        total_sum = sum(item.get('price', 0) for item in cart)
        flash(f"✅ Продано билетов: {len(cart)} на сумму {total_sum} руб.")
        # Очищаем корзину
        redis_conn.set_cart(user_id, [])
    else:
        flash(f"❌ Ошибка: {res.error_message}")

    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))


@ticket_cart_bp.route("/clear_ticket_cart", methods=["POST"])
@login_required
@role_required
def clear_ticket_cart():
    """Очистка корзины"""
    user_data = session.get("user")
    if not user_data:
        flash("❌ Пользователь не найден")
        return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

    user_id = user_data["user_id"]
    redis_conn.set_cart(user_id, [])
    flash("🗑️ Корзина очищена")
    
    return redirect(url_for("ticket_cart_bp.ticket_cart_get"))

