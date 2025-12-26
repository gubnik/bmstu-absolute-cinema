from flask import Blueprint, flash, render_template, request
import os
from database.sql_provider import SQLProvider
from decorators import login_required, role_required
from load_config import load_env_config
from translation import t
from .model_route import model_get_ticket_report, model_add_ticket_report
from blueprints.model_response import Ok, Error


ticket_report_bp = Blueprint('ticket_report_bp', __name__, template_folder='templates')


@ticket_report_bp.route('/ticket_report', methods=['GET'])
@login_required
@role_required
def ticket_report_input_handler():
    return render_template("ticket_report.html")


@ticket_report_bp.route('/ticket_report', methods=['POST'])
@login_required
@role_required
def ticket_report_post_handler():
    user_data = request.form
    year = user_data.get('year')
    month = user_data.get('month')
    action = user_data.get('action')

    try:
        year = int(year) # pyright: ignore
        month = int(month) # pyright: ignore
    except (TypeError, ValueError):
        return render_template("ticket_report.html", 
                             form_data=user_data)

    db_config = load_env_config("DB_CONFIG")
    provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    report_types = ["ticket_count", "total_revenue", "sessions_avgprice", "all"]

    try:
        match action:
            case 'add':
                res_info = model_add_ticket_report(db_config, user_data, report_types, provider)
                match res_info:
                    case Ok():
                        flash(res_info.result, category="ok")
                        return render_template("ticket_report.html",
                                         form_data=user_data)
                    case Error():
                        flash(res_info.error, category="error")
                        return render_template("ticket_report.html",
                                         form_data=user_data)
            case 'get':
                res_info = model_get_ticket_report(db_config, user_data, report_types, provider)
                match res_info:
                    case Ok():
                        report_title=t("reports.label.general_report_title", month=user_data.get('month'), year=user_data.get('year'))
                        return render_template("dynamic.html",
                                             prod_title=report_title,
                                             products=res_info.result,
                                             data_type='ticket_report')
                    case Error():
                        return render_template("error.html",
                                             error_message=t("reports.label.no_data"))
            case _:
                flash(t("reports.label.unknown_action", action=action), category="error")
                return render_template("ticket_report.html", 
                                 form_data=user_data)
    except Exception as e:
        flash(t("reports.label.system_error", cause=str(e)), category="error")
        return render_template("ticket_report.html", 
                             form_data=user_data)

