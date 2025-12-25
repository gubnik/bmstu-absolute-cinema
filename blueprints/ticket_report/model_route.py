from pymysql import DatabaseError
from database.select import select_dict
from dataclasses import dataclass
from database.DBcm import DBContextManager
from blueprints.model_response import ModelResponse, ResponseOk, ResponseError
from translation import t


@dataclass
class SuccessMessage:
    msg: str

@dataclass
class ErrorMessage:
    err: str

SimpleMessage = SuccessMessage | ErrorMessage

@dataclass
class TicketReportResponse:
    result: list
    msg: str
    status: bool


def model_get_ticket_report(db_config, user_input_data, sql_provider) -> ModelResponse:
    """Получить отчёт по продажам билетов за месяц/год"""
    try:
        required_fields = ['year', 'month']
        
        for field in required_fields:
            if field not in user_input_data or not user_input_data[field]:
                return ResponseError(t("reports.label.empty_field", field=field))
    
        _sql = sql_provider.get('report.sql')
        params = (
            user_input_data['year'],
            user_input_data['month'],
        )
        result = select_dict(db_config, _sql, params)
        if result:
            return ResponseOk(result)
        return ResponseError(t("reports.label.no_data"))
    except Exception as e:
        return ResponseError(t("reports.label.db_general_error", cause=str(e)))


def model_add_ticket_report(db_config, user_input_data, sql_provider) -> SimpleMessage:
    """Сформировать отчёт по продажам билетов за месяц/год"""
    try:
        required_fields = ['year', 'month']
        for field in required_fields:
            if field not in user_input_data or not user_input_data[field]:
                return ErrorMessage(t("reports.label.empty_field", field=field))
        year = user_input_data['year']
        month = user_input_data['month']
        _sql = sql_provider.get('add_report.sql')
        params = (year, month)
        with DBContextManager(db_config) as cursor:
            if cursor is None:
                return ErrorMessage(t("reports.label.db_connection_error"))
            cursor.execute(_sql, params)
            cursor.execute("SELECT @p_success")
            status_r = cursor.fetchone()
            if not status_r or status_r[0] is None or status_r[0] != 1:
                raise DatabaseError()
            return SuccessMessage(t("reports.label.success"))
    except Exception as e:
        return ErrorMessage(t("reports.label.db_general_error", cause=str(e)))

