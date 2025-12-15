from dataclasses import dataclass
from database.select import select_dict


@dataclass
class FilmInfoResponse:
    result: list
    error_message: str
    status: bool


def model_films_search(db_config, search_type, search_value, sql_provider):
    """Поиск фильмов по разным критериям"""
    try:
        if search_type == 'year':
            _sql = sql_provider.get('films_by_year.sql')
            result = select_dict(db_config, _sql, (search_value,))
        elif search_type == 'country':
            _sql = sql_provider.get('films_by_country.sql')
            result = select_dict(db_config, _sql, (f'%{search_value}%',))
        elif search_type == 'director':
            _sql = sql_provider.get('films_by_director.sql')
            result = select_dict(db_config, _sql, (f'%{search_value}%',))
        else:
            return FilmInfoResponse([], 'Неверный тип поиска', False)
        
        if result:
            return FilmInfoResponse(result, '', True)
        return FilmInfoResponse([], 'Фильмы не найдены', False)
    except Exception as e:
        return FilmInfoResponse([], str(e), False)

