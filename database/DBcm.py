from types import TracebackType
from typing import Self, Type
from pymysql import Connection, connect

from pymysql.cursors import Cursor
from pymysql.err import OperationalError

import traceback
import inspect 

class DBContextManager:

    def __init__(self: Self, db_config: dict):
        self.conn: Connection | None = None
        self.cursor: Cursor | None = None
        self.db_config = db_config

    def __enter__(self: Self):
        try:
            self.conn = connect(**self.db_config)
            self.cursor = self.conn.cursor()
            return self.cursor
        except OperationalError as err:
            print(f"DB config: {self.db_config}")
            print("Operational error:", err.args)
            return None

    def __exit__(self: Self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType):
        if exc_type:
            print("DBcm error", exc_type, exc_val, exc_tb)
            # Unwrap exceptions to see what's going on
            for frame, _ in traceback.walk_tb(exc_tb):
                info = inspect.getframeinfo(frame)
                print(info)
        if not self.conn:
            return True
        if self.cursor:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.cursor.close()
        return True

