from pymysql import DatabaseError
from database.select import select_dict
from dataclasses import dataclass
from database.DBcm import DBContextManager
from blueprints.model_response import (
    Result,
    Ok,
    Error,
)
from translation import t

@dataclass
class TicketReportResponse:
    result: list
    msg: str
    status: bool


def model_get_ticket_report(db_config, user_input_data, report_types, sql_provider) -> Result[list[dict], str]:
    """Получить отчёт по продажам билетов за месяц/год"""
    required_fields = ['year', 'month']
    
    for field in required_fields:
        if field not in user_input_data or not user_input_data[field]:
            return Error(t("reports.label.empty_field", field=field))

    params = (
        user_input_data['year'],
        user_input_data['month'],
    )
    report_type = user_input_data["report_type"]
    
    if report_type in report_types:
        _sql = sql_provider.get(f'get_{report_type}_report.sql')
        result = select_dict(db_config, _sql, params)
        if result:
            return Ok(result)
    else:
        return Error(t("reports.label.bad_report_type"))
    return Error(t("reports.label.no_data"))


def model_add_ticket_report(db_config, user_input_data,  report_types, sql_provider) -> Result[str, str]:
    """Сформировать отчёт по продажам билетов за месяц/год"""
    required_fields = ['year', 'month']
    for field in required_fields:
        if field not in user_input_data or not user_input_data[field]:
            return Error(t("reports.label.empty_field", field=field))
    year = user_input_data['year']
    month = user_input_data['month']
    report_type = user_input_data["report_type"]
    if report_type in report_types:
        _sql = sql_provider.get(f'add_{report_type}_report.sql')
        params = (year, month)
        with DBContextManager(db_config) as cursor:
            if cursor is None:
                return Error(t("reports.label.db_connection_error"))
            try:
                cursor.execute(_sql, params)
                cursor.execute("SELECT @p_success")
                status_r = cursor.fetchone()
                if not status_r or status_r[0] is None or status_r[0] != 1:
                    raise DatabaseError()
                return Ok(t("reports.label.success"))
            except Exception as e:
                return Error(t("reports.label.db_general_error", cause=str(e)))
    else:
        return Error(t("reports.label.bad_report_type"))

