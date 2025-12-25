from flask import Blueprint, render_template
from decorators import login_required, role_required


queries_menu_bp = Blueprint('queries_menu_bp', __name__, template_folder='templates')


@queries_menu_bp.route('/queries_menu', methods=['GET'])
@login_required
@role_required
def queries_menu_handler():
    """Меню запросов"""
    return render_template("queries_menu.html")

