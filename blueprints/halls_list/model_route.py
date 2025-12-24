from database.select import select_dict
from translation import get_locale, t
from blueprints.model_response import ModelResponse, ResponseOk, ResponseError
from database.sql_provider import SQLProvider
from load_config import load_env_config
import os


def model_halls_list() -> ModelResponse:
    """Получить список залов с информацией"""
    db_config = load_env_config("DB_CONFIG")
    sql_provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    try:
        _sql = sql_provider.get('halls_list.sql')
        result = select_dict(db_config, _sql, params=(get_locale(),))
        if result:
            return ResponseOk([{
                **hp,
                "price_range": f'{hp["price_range"]} {t("global.rubles")}'
            } for hp in result])
        return ResponseError(t("halls.label.no_halls"))
    except Exception as e:
        return ResponseError(str(e))

