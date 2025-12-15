from types import TracebackType
from pymysql import connect

from pymysql.err import OperationalError

import traceback
import inspect 

class DBContextManager:

    def __init__(self, db_config: dict):
        self.conn = None
        self.cursor = None
        self.db_config = db_config

    def __enter__(self):
        try:
            self.conn = connect(**self.db_config)
            self.cursor = self.conn.cursor()
            return self.cursor
        except OperationalError as err:
            print("Operational error:", err.args)
            return None

    def __exit__(self, exc_type, exc_val, exc_tb: TracebackType):
        if exc_type:
            print("DBcm error", exc_type, exc_val, exc_tb)
            for frame, lineno in traceback.walk_tb(exc_tb):
                info = inspect.getframeinfo(frame)
                print(info)
        if self.cursor:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.cursor.close()
        return True

