from dataclasses import fields, is_dataclass
from typing import Any, Callable, Iterator, Sequence, Type, TypeVar
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
                 converters: dict[str, Converter] | None = None
                 ) -> Iterator[T]:
    """
    Creates a lazy iterator for a DB query
    """
    if not is_dataclass(cls):
        raise TypeError("cls must be a dataclass type")
    field_names: list[str] = [f.name.lower() for f in fields(cls)]
    conv = {k.lower(): v for k, v in (converters or {}).items()}
    
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError("Cursor not created")
        if params:
            cursor.execute(_sql, params)
        else:
            cursor.execute(_sql)
        desc = cursor.description or []
        col_index: dict[str, int] = {col[0].lower(): i for i, col in enumerate(desc)}

        field_indices: dict[str, int | None] = {
            name: col_index.get(name) for name in field_names
        }
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                kwargs = {}
                for name in field_names:
                    idx = field_indices[name]
                    val = row[idx] if idx is not None else None
                    conv_fn = conv.get(name)
                    kwargs[name] = conv_fn(val) if conv_fn and val is not None else val
                try:
                    yield cls(**kwargs)
                except TypeError as e:
                    raise TypeError(f"Could not initialize {cls.__name__} with {kwargs}") from e


def select_typed(cls: Type[T],
                 db_config: dict,
                 _sql: str,
                 params: Sequence[Any] | None = None,
                 *,
                 batch_size: int = 512,
                 converters: dict[str, Converter] | None = None
                 ) -> list[T]:
    return [i for i in iterate_select_typed(cls=cls, db_config=db_config, _sql=_sql, params=params, batch_size=batch_size, converters=converters)]
