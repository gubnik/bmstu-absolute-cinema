from dataclasses import dataclass
from database.select import select_dict


@dataclass
class HallsInfoResponse:
    result: list
    error_message: str
    status: bool


def model_halls_list(db_config, sql_provider):
    """Получить список залов с информацией"""
    try:
        _sql = sql_provider.get('halls_list.sql')
        result = select_dict(db_config, _sql)
        if result:
            return HallsInfoResponse(result, '', True)
        return HallsInfoResponse([], 'Залы не найдены', False)
    except Exception as e:
        return HallsInfoResponse([], str(e), False)

