import psycopg2
import sys

class PgConnection:
    
    def __init__(self, log, pgconnparam):
        self.result = None
        self.log = log
        self.myconnection = "dbname=" + pgconnparam['dbconnname'] + " " + "user=" + pgconnparam['dbconnuser'] + " " + "host=" + pgconnparam['dbendpoint'] \
                 + " " + "port=" + pgconnparam['dbconnport'] + " " + "password=" + pgconnparam['dbconnpass']

    def connect_to_db(self, query):
        try:
            db_connection = psycopg2.connect(self.myconnection)
            db_cursor = db_connection.cursor()
            db_cursor.execute(query)
            result = db_cursor.fetchall()
            print("query_result")
            print(result)
        except Exception as err:
            self.log.error(err)
            error_message = dict()
            error_message['error'] = str(err)
            return error_message
        finally:
            db_cursor.close()
            db_connection.close()
        return result
