import psycopg2
import sys
from database_exceptions import DataBaseException

class PgConnection:
    
    def __init__(self, log, pgconnparam):
        self.result = None
        self.log = log
        self.myconnection = "dbname={0} user={1} host={2} port={3} password={4}".format(pgconnparam['dbconnname'], 
                                pgconnparam['dbconnuser'], pgconnparam['dbendpoint'], 
                                pgconnparam['dbconnport'], pgconnparam['dbconnpass'])

    def get_result_from_db(self, query):
        try:
            db_connection = psycopg2.connect(self.myconnection)
            db_cursor = db_connection.cursor()
            db_cursor.execute(query)
            result = db_cursor.fetchall()
            self.log.info(result)
        except Exception as err:
            self.log.error(err)
            raise DataBaseException("Error while making DB connection or executing query")
        finally:
            db_cursor.close()
            db_connection.close()
        return result
