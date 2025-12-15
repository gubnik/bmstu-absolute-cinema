from flask import Blueprint, render_template, request
import json
import os
from database.sql_provider import SQLProvider
from decorators import login_required, role_required
from .model_route import model_add_ticket_report, model_get_ticket_report

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
    print("User data: ", user_data)
    year = user_data.get('year')
    month = user_data.get('month')
    action = user_data.get('action')  # 'add' или 'get'

    try:
        year = int(year)
        month = int(month)
    except (TypeError, ValueError):
        return render_template("ticket_report.html", 
                             error_message="Неверный формат года или месяца", 
                             form_data=user_data)

    with open("data/dbconfig.json") as f:
        db_config = json.load(f)

    provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

    try:
        if action == 'add':
            res_info = model_add_ticket_report(db_config, user_data, provider)
            print("res_info.result = ", res_info.result)
            if res_info.status:
                return render_template("ticket_report.html",
                                     success_message='Отчет успешно сформирован',
                                     form_data={})
            else:
                return render_template("ticket_report.html",
                                     error_message=res_info.error_message,
                                     form_data=user_data)

        elif action == 'get':
            res_info = model_get_ticket_report(db_config, user_data, provider)
            print("res_info.result = ", res_info.result)

            # Переименовываем колонки для отображения
            for row in res_info.result:
                row['ID отчёта'] = row.pop('report_id', '')
                row['Месяц'] = row.pop('report_month', '')
                row['Год'] = row.pop('report_year', '')
                row['Продано билетов'] = row.pop('total_tickets_sold', '')
                row['Выручка (руб.)'] = row.pop('total_revenue', '')
                row['Сеансов'] = row.pop('sessions_count', '')
                row['Ср. цена билета'] = row.pop('avg_ticket_price', '')
                row['Дата отчёта'] = row.pop('created_at', '')

            if res_info.status:
                if res_info.result:
                    report_title = f"🎟️ Отчет по продажам билетов за {user_data.get('month')}/{user_data.get('year')}"
                    return render_template("dynamic.html",
                                         prod_title=report_title,
                                         products=res_info.result,
                                         data_type='ticket_report')
                else:
                    return render_template("error.html",
                                         error_message="По вашему запросу данных не найдено. Сначала сформируйте отчёт.")
            else:
                return render_template("error.html",
                                     error_message=res_info.error_message or "Произошла ошибка при выполнении запроса.")
        else:
            return render_template("ticket_report.html", 
                                 error_message="Неизвестное действие", 
                                 form_data=user_data)

    except Exception as e:
        return render_template("ticket_report.html", 
                             error_message=f"Системная ошибка: {str(e)}", 
                             form_data=user_data)

