from flask import Blueprint, render_template, request
from decorators import login_required, role_required
from translation import t
from .model_route import SessionBrief, model_available_seats, model_get_sessions

available_seats_bp = Blueprint('available_seats_bp', __name__, template_folder='templates')


@available_seats_bp.route('/available_seats', methods=['GET'])
@login_required
@role_required
def available_seats_handler():
    """Страница выбора сеанса для просмотра свободных мест"""
    sessions: list[SessionBrief] | None = model_get_sessions()
    return render_template("available_seats.html", sessions=sessions)


@available_seats_bp.route('/available_seats', methods=['POST'])
@login_required
@role_required
def available_seats_result_handler():
    """Обработка запроса свободных мест"""
    user_data = request.form
    session_id = user_data.get('session_id')
    res_info = model_available_seats(session_id)
    if res_info.result:
        return render_template("dynamic.html",
                               prod_title=t("seats.label.header"),
                               products=res_info.result)
    else:
        return render_template("error.html",
                                error_message=res_info.error_message or t("seats.lable.no_seats"))

