from flask import Blueprint, render_template
import json
import os
from database.sql_provider import SQLProvider
from decorators import login_required, role_required
from .model_route import model_halls_list

halls_list_bp = Blueprint('halls_list_bp', __name__, template_folder='templates')


@halls_list_bp.route('/halls_list', methods=['GET'])
@login_required
@role_required
def halls_list_handler():
    """Страница со списком залов"""
    with open("data/dbconfig.json") as f:
        db_config = json.load(f)
    
    provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    
    try:
        res_info = model_halls_list(db_config, provider)
        
        if res_info.status and res_info.result:
            return render_template("dynamic.html",
                                  prod_title='🏛️ Залы кинотеатра',
                                  products=res_info.result)
        else:
            return render_template("error.html",
                                  error_message=res_info.error_message or "Залы не найдены")
    
    except Exception as e:
        print(f"Error in halls_list_handler: {e}")
        return render_template("error.html",
                              error_message=f"Системная ошибка: {str(e)}")

