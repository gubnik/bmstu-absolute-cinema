from flask import Blueprint, render_template, request
from decorators import login_required, role_required
from translation import t
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
    search_type = user_data.get('search_type')
    search_value = user_data.get('search_value', '').strip()
    res_info = model_films_search(search_type, search_value)
    if res_info.result:
        return render_template("dynamic.html",
                               prod_title=t("films.label.result"),
                               products=res_info.result)
    else:
        return render_template("error.html",
                               error_message=res_info.error_message or t("films.label.no_films"))

