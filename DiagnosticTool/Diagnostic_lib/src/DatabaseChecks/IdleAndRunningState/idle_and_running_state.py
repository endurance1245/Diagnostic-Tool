activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

import logging

from campaign_db_connection import PgConnection
from db_parameters import DbParameters
from database_exceptions import DBParameterNotFoundException, DataBaseException
from db_queries import db_query_for_running_state, db_query_for_idle_state

class IdleRunningState:

    def __init__(self, campaign_host):
        self.campaign_host = campaign_host

    def get_running_queries(self):
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
                db_query_result = db_connection_obj.get_result_from_db(db_query_for_running_state)
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result == []:
                result["Running Queries"] = "No query"
            else:
                result_rows = []
                for row in db_query_result:
                    r = self.make_result(row)
                    result_rows.append(r)
                result["Running Queries"] = result_rows
        return result

    def get_idle_queries(self):
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
                db_query_result = db_connection_obj.get_result_from_db(db_query_for_idle_state)
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result == []:
                result["Idle Queries"] = "No query"
            else:
                result_rows = []
                for row in db_query_result:
                    r = self.make_result(row)
                    result_rows.append(r)
                result["Idle Queries"] = result_rows
        return result

    def make_result(self, row):
        result = {}
        result["pid"] = row[0]
        result["duration"] = str(row[1])
        result["query"] = row[2]
        return result
