from flask import Blueprint, render_template
from blueprints.model_response import ModelResponse, ResponseError
from decorators import login_required, role_required
from translation import t
from .model_route import model_halls_list
from blueprints.model_response import ResponseOk, ResponseError

halls_list_bp = Blueprint('halls_list_bp', __name__, template_folder='templates')


@halls_list_bp.route('/halls_list', methods=['GET'])
@login_required
@role_required
def halls_list_handler():
    """Страница со списком залов"""
    
    res_info: ModelResponse = model_halls_list()
    match res_info:
        case ResponseOk():
            return render_template("dynamic.html",
                              prod_title='🏛️ Залы кинотеатра',
                              products=res_info.result)
        case ResponseError():
            return render_template("error.html",
                              error_message=res_info.error or t("halls.label.no_halls"))

