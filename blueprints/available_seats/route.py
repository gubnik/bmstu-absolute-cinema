from flask import Blueprint, render_template, request
import json
import os
from database.sql_provider import SQLProvider
from database.select import select_dict
from decorators import login_required, role_required
from .model_route import model_available_seats, model_get_sessions

available_seats_bp = Blueprint('available_seats_bp', __name__, template_folder='templates')


@available_seats_bp.route('/available_seats', methods=['GET'])
@login_required
@role_required
def available_seats_handler():
    """Страница выбора сеанса для просмотра свободных мест"""
    with open("data/dbconfig.json") as f:
        db_config = json.load(f)
    
    provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    sessions = model_get_sessions(db_config, provider)
    
    return render_template("available_seats.html", sessions=sessions)


@available_seats_bp.route('/available_seats', methods=['POST'])
@login_required
@role_required
def available_seats_result_handler():
    """Обработка запроса свободных мест"""
    user_data = request.form
    
    with open("data/dbconfig.json") as f:
        db_config = json.load(f)
    
    provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    session_id = user_data.get('session_id')
    
    try:
        res_info = model_available_seats(db_config, session_id, provider)
        
        if res_info.status and res_info.result:
            return render_template("dynamic.html",
                                  prod_title='💺 Свободные места на сеанс',
                                  products=res_info.result)
        else:
            return render_template("error.html",
                                  error_message=res_info.error_message or "Свободные места не найдены")
    
    except Exception as e:
        print(f"Error in available_seats_result_handler: {e}")
        return render_template("error.html",
                              error_message=f"Системная ошибка: {str(e)}")

