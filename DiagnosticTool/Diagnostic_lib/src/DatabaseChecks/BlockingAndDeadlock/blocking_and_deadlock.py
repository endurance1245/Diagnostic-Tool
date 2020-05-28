activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

import logging
from campaign_db_connection import PgConnection
from db_parameters import DbParameters
from database_exceptions import DBParameterNotFoundException, DataBaseException
from db_queries import db_query_for_max_connection, db_query_for_blocking, db_query_for_deadlock_count, db_query_for_acquired_lock_modes

class BlockingDeadlock:

    def __init__(self, campaign_host):
        self.campaign_host = campaign_host
    
    def get_blocking_queries(self):
        try:
            params_obj = DbParameters()
            params = params_obj.get_db_parameters()
        except DBParameterNotFoundException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        if "error" in params:
            return params
        else:
            result = {}
            db_connection_obj = PgConnection(logging, params)
            try:
                db_query_result = db_connection_obj.get_result_from_db(db_query_for_max_connection)
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result == []:
                result["blocking query result"] = "No blocking queries"
            else:
                connection_count = db_query_result[0][0]    #Check for max_connection, threshold is 64
                if connection_count < 64:                   #If max_connection is less than 64, blocking is less like to be present
                    result["blocking query result"] = "No blocking queries"
                else:
                    try:
                        db_query_result = db_connection_obj.get_result_from_db(db_query_for_blocking)
                    except DataBaseException as err:
                        logging.error(err)
                        error_message = dict()
                        error_message["error"] = str(err)
                        return error_message
                    if db_query_result == []:
                        result["blocking query result"] = "No blocking queries"
                    else:
                        result = []
                        for row in db_query_result:
                            r = self.make_result_for_blocking(row) #form dictionary from the returned row of db
                            result.append(r)
        return result

    def get_deadlock_queries(self):
        try:
            params_obj = DbParameters()
            params = params_obj.get_db_parameters()
        except DBParameterNotFoundException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        if "error" in params:
            return params
        else:
            db_connection_obj = PgConnection(logging, params)
            result = {}
            try:
                db_query_result = db_connection_obj.get_result_from_db(db_query_for_deadlock_count)
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result == []:
                result["Deadlock Result"] = "No Deadlock"
            else:
                result["Deadlock count"] = db_query_result[0][0]
            
            try:
                db_query_result = db_connection_obj.get_result_from_db(db_query_for_acquired_lock_modes)
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result == []:
                result["Acquired Locks"] = "No Acquired Locks"
            else:
                result_rows = []
                for row in db_query_result:
                    r = self.make_result_for_lock_modes(row)
                    result_rows.append(r)
                result["Modes of Acquired Locks"] = result_rows
        return result
    
    def make_result_for_blocking(self, row):
        result = {}
        result["blocked_pid"] = row[0]
        result["blocked_user"] = row[1]
        result["blocking_statement"] = row[2]
        result["blocking_duration"] = str(row[3])
        result["blocking_pid"] = row[4]
        result["blocking_user"] = row[5]
        result["blocked_statement"] = row[6]
        result["blocked_duration"] = str(row[7])
        return result

    def make_result_for_lock_modes(self, row):
        result = {}
        result["virtualtransaction"] = row[0]
        result["relation"] = row[1]
        result["locktype"] = row[2]
        #result["page"] = str(row[3]) 
        #result["tuple"] = row[4]
        result["mode"] = row[5]
        result["granted"] = row[6]
        result["transactionid"] = row[7]
        return result
