import logging
import os
import json
import subprocess
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
                    r = self.make_result_for_runnning(row)
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
                    r = self.make_result_for_idle(row)
                    result_rows.append(r)
                result["Idle Queries"] = result_rows
        git return result

    def make_result_for_running(self, row):
        result = {}
        result["running_pid"] = row[0]
        result["running_duration"] = str(row[1])
        result["running_query"] = row[2]
        return result

    def make_result_for_idle(self, row):
        result = {}
        result = {}
        result["idle_pid"] = row[0]
        result["idle_duration"] = str(row[1])
        result["idle_query"] = row[1]
        return result


    