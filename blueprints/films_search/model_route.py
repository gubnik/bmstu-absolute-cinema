from database.select import select_dict
from database.sql_provider import SQLProvider
from translation import t, get_locale
from load_config import load_env_config
from blueprints.model_response import ModelResponse, ResponseOk, ResponseError
import os


def model_films_search(search_type: str | None, search_value) -> ModelResponse:
    db_config = load_env_config("DB_CONFIG")
    sql_provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
    """Поиск фильмов по разным критериям"""
    try:
        result: list[dict] | None = None
        criteria_do_wrap = {'year': False, 'director': True, 'country': True}
        chosen_criteria: str | None = None
        if search_type in criteria_do_wrap:
            sanitized_value = search_value if not criteria_do_wrap[search_type] else f"%{search_value}%"
            locale = get_locale()
            _sql = sql_provider.get(f'films_by_{search_type}.sql')
            result = select_dict(db_config, _sql, params=(locale, sanitized_value,))
            chosen_criteria = search_type
        if not chosen_criteria:
            return ResponseError(t("films.label.bad_search"))
        if not result:
            return ResponseError(t("films.label.no_films"))
        return ResponseOk([{**d, "duration": f'{d["duration"]} {t("global.minutes")}'} for d in result])
    except Exception as e:
        return ResponseError(str(e))

