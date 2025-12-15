from flask import Blueprint, render_template, request
import json
import os
from database.sql_provider import SQLProvider
from decorators import login_required, role_required
from .model_route import model_films_search

films_search_bp = Blueprint('films_search_bp', __name__, template_folder='templates')


@films_search_bp.route('/films_search', methods=['GET'])
@login_required
@role_required
def films_search_handler():
    """Страница поиска фильмов"""
    return render_template("films_search.html")


@films_search_bp.route('/films_search', methods=['POST'])
@login_required
@role_required
def films_search_result_handler():
    """Обработка поиска фильмов"""
    user_data = request.form
    
    with open("data/dbconfig.json") as f:
        db_config = json.load(f)
    
    provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    
    search_type = user_data.get('search_type')
    search_value = user_data.get('search_value', '').strip()
    
    try:
        res_info = model_films_search(db_config, search_type, search_value, provider)
        
        if res_info.status and res_info.result:
            return render_template("dynamic.html",
                                  prod_title='🎬 Результаты поиска фильмов',
                                  products=res_info.result)
        else:
            return render_template("error.html",
                                  error_message=res_info.error_message or "Фильмы не найдены")
    
    except Exception as e:
        print(f"Error in films_search_result_handler: {e}")
        return render_template("error.html",
                              error_message=f"Системная ошибка: {str(e)}")

