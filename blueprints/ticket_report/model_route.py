from database.select import select_dict
from dataclasses import dataclass
from database.DBcm import DBContextManager


@dataclass
class TicketReportResponse:
    result: list
    error_message: str
    status: bool


def model_get_ticket_report(db_config, user_input_data, sql_provider):
    """Получить отчёт по продажам билетов за месяц/год"""
    error_message = ''
    required_fields = ['year', 'month']
    
    for field in required_fields:
        if field not in user_input_data or not user_input_data[field]:
            error_message = f"Не заполнено обязательное поле: {field}"
            return TicketReportResponse([], error_message=error_message, status=False)

    _sql = sql_provider.get('report.sql')
    params = (
        user_input_data['year'],
        user_input_data['month'],
    )
    print("sql=", _sql)
    print("params=", params)

    result = select_dict(db_config, _sql, params)

    if result:
        return TicketReportResponse(result, error_message=error_message, status=True)

    return TicketReportResponse([], error_message=error_message, status=False)


def model_add_ticket_report(db_config, user_input_data, sql_provider):
    """Сформировать отчёт по продажам билетов за месяц/год"""
    error_message = ''

    required_fields = ['year', 'month']
    for field in required_fields:
        if field not in user_input_data or not user_input_data[field]:
            error_message = f"Не заполнено обязательное поле: {field}"
            return TicketReportResponse([], error_message=error_message, status=False)

    year = user_input_data['year']
    month = user_input_data['month']

    _sql = sql_provider.get('add_report.sql')
    params = (year, month)

    print("sql =", _sql)
    print("params =", params)

    with DBContextManager(db_config) as cursor:
        if cursor is None:
            return TicketReportResponse([], error_message="Ошибка подключения к БД", status=False)

        try:
            cursor.execute(_sql, params)

            cursor.execute("SELECT @p_error_message AS err")
            row = cursor.fetchone()

            if row and row[0]:
                warning = row[0]
                return TicketReportResponse(
                    [],
                    error_message=warning,
                    status=False
                )

            return TicketReportResponse(
                [{'message': 'Отчёт успешно создан'}],
                error_message='',
                status=True
            )

        except Exception as e:
            return TicketReportResponse(
                [],
                error_message=f"Ошибка БД: {str(e)}",
                status=False
            )

