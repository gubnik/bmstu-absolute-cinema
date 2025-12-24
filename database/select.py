from dataclasses import fields, is_dataclass
from typing import Any, Callable, Iterator, Sequence, Type, TypeVar

from flask import current_app
from database.DBcm import DBContextManager
from pymysql.err import OperationalError

T = TypeVar("T")

def select_list(db_config: dict, _sql: str, params: Sequence[Any] | None = None):
    result = ()
    schema = []
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError("Cursor not created")
        else:
            try:
                if params:
                    current_app.logger.debug(f"Cursor with params {params} working")
                    cursor.execute(_sql, params)
                else:
                    cursor.execute(_sql)
                result = cursor.fetchall()
            except OperationalError as error:
                print("error: ", error.args)
                return result, schema
            else:
                print("Cursor finished with no errors")
            schema = [item[0] for item in cursor.description]
    return result, schema


def select_dict(db_config: dict, _sql: str, params: Sequence[Any] | None = None) -> list[dict]:
    result, schema = select_list(db_config, _sql, params)
    return [dict(zip(schema, item)) for item in result]


Converter = Callable[[Any], Any]


def iterate_select_typed(cls: Type[T],
                         db_config: dict,
                         _sql: str,
                         params: Sequence[Any] | None = None,
                         *,
                         batch_size: int = 512,
                         converters: dict[str, Converter] | None = None,
                         columns_map: dict[str, str] | None = None  # dataclass_field -> column_name
                         ) -> Iterator[T]:
    if not is_dataclass(cls):
        raise TypeError("cls must be a dataclass type")
    field_names = [f.name for f in fields(cls)]
    conv = {k.lower(): v for k, v in (converters or {}).items()}
    columns_map_norm = {k: v for k, v in (columns_map or {}).items()}

    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise RuntimeError("DBContextManager returned no cursor")

        if params:
            current_app.logger.debug(f"Cursor with params {params} working")
            cursor.execute(_sql, params)
        else:
            cursor.execute(_sql)

        desc = cursor.description or []
        col_index = {col[0].lower(): i for i, col in enumerate(desc)}

        field_indices: dict[str, int | None] = {}
        for name in field_names:
            if name in columns_map_norm:
                col_name = columns_map_norm[name].lower()
                idx = col_index.get(col_name)
            else:
                idx = col_index.get(name.lower())
            field_indices[name] = idx

        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                kwargs: dict[str, Any] = {}
                for name in field_names:
                    idx = field_indices[name]
                    val = None if idx is None else row[idx]
                    conv_fn = conv.get(name.lower())
                    kwargs[name] = conv_fn(val) if conv_fn and val is not None else val
                try:
                    yield cls(**kwargs)
                except TypeError as e:
                    raise TypeError(f"Failed to instantiate {cls.__name__} with {kwargs}") from e


def select_typed(cls: Type[T],
                 db_config: dict,
                 _sql: str,
                 params: Sequence[Any] | None = None,
                 *,
                 batch_size: int = 512,
                 columns_map: dict[str, str] | None = None,
                 converters: dict[str, Converter] | None = None
                 ) -> list[T]:
    return [i for i in iterate_select_typed(cls=cls,
                                            db_config=db_config,
                                            _sql=_sql,
                                            params=params,
                                            batch_size=batch_size,
                                            columns_map=columns_map,
                                            converters=converters)]
