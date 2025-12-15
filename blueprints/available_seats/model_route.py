from dataclasses import dataclass
from database.select import select_dict


@dataclass
class SeatsInfoResponse:
    result: list
    error_message: str
    status: bool


def model_get_sessions(db_config, sql_provider):
    """Получить список доступных сеансов"""
    try:
        _sql = sql_provider.get('get_sessions.sql')
        result = select_dict(db_config, _sql)
        return result
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return []


def model_available_seats(db_config, session_id, sql_provider):
    """Получить свободные места на сеанс"""
    try:
        _sql = sql_provider.get('available_seats.sql')
        result = select_dict(db_config, _sql, (session_id,))
        if result:
            return SeatsInfoResponse(result, '', True)
        return SeatsInfoResponse([], 'Свободные места не найдены или билеты ещё не сгенерированы', False)
    except Exception as e:
        return SeatsInfoResponse([], str(e), False)

