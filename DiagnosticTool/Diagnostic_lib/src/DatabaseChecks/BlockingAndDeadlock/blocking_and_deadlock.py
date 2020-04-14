import logging
import os
import json
import subprocess
import ast
from campaign_db_connection import PgConnection
from newrelic_connection import NewRelicInsight
from database_exceptions import DBParameterNotFoundException

class BlockingDeadlock:

    def __init__(self, campaign_host):
        self.campaign_host = campaign_host
        self.db_connection_port = "5432"
    
    def get_blocking_queries(self):
        try:
            params = self.get_db_parameters()
        except DBParameterNotFoundException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        if "error" in params:
            return params
        else:
            result = {}
            db_query_for_max_connection = "SELECT COUNT(*) connections_awaiting_lock FROM pg_locks WHERE granted = false GROUP BY pid;"
            db_connection_obj = PgConnection(logging, params)
            db_query_result = db_connection_obj.connect_to_db(db_query_for_max_connection)
            if "error" in db_query_result:
                return db_query_result
            elif db_query_result == []:
                result["blocking query result"] = "No blocking queries"
            else:
                connection_count = db_query_result[0][0]    #Check for max_connection, threshold is 64
                if connection_count < 64:                   #If max_connection is less than 64, blocking is less like to be present
                    result["blocking query result"] = "No blocking queries"
                else:
                    db_query_for_blocking = "SELECT blocked_locks.pid AS blocked_pid, " \
                        "blocked_activity.usename AS blocked_user, blocking_activity.query AS blocking_statement, " \
                        "now() - blocking_activity.query_start AS blocking_duration, blocking_locks.pid AS blocking_pid, " \
                        "blocking_activity.usename AS blocking_user, blocked_activity.query AS blocked_statement, " \
                        "now() - blocked_activity.query_start AS blocked_duration FROM pg_catalog.pg_locks AS blocked_locks " \
                        "JOIN pg_catalog.pg_stat_activity AS blocked_activity ON blocked_activity.pid = blocked_locks.pid " \
                        "JOIN pg_catalog.pg_locks AS blocking_locks ON blocking_locks.locktype = blocked_locks.locktype " \
                        "AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE " \
                        "AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation " \
                        "AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page " \
                        "AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple " \
                        "AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid " \
                        "AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid " \
                        "AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid " \
                        "AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid " \
                        "AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid " \
                        "AND blocking_locks.pid != blocked_locks.pid " \
                        "JOIN pg_catalog.pg_stat_activity AS blocking_activity ON blocking_activity.pid = blocking_locks.pid " \
                        "WHERE NOT blocked_locks.granted;"
                    db_query_result = db_connection_obj.connect_to_db( db_query_for_blocking)
                    if "error" in db_query_result:
                        return db_query_result
                    elif db_query_result == []:
                        result["blocking query result"] = "No blocking queries"
                    else:
                        result = []
                        for row in db_query_result:
                            r = self.make_result_for_blocking(row) #form dictionary from the returned row of db
                            result.append(r)
        return result

    def get_deadlock_queries(self):
        try:
            params = self.get_db_parameters()
        except DBParameterNotFoundException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        if "error" in params:
            return params
        else:
            db_query_for_deadlock_count = "SELECT deadlocks, datname FROM pg_stat_database WHERE datname = current_database();"
            db_connection_obj = PgConnection(logging, params)
            db_query_result = db_connection_obj.connect_to_db(db_query_for_deadlock_count)
            result = {}
            if "error" in db_query_result:
                return db_query_result
            elif db_query_result == []:
                result["Deadlock Result"] = "No Deadlock"
            else:
                result["Deadlock count"] = db_query_result[0][0]

            db_query_for_acquired_lock_modes = "SELECT virtualtransaction, relation::regclass, locktype, page, " \
                                "tuple, mode, granted, transactionid FROM pg_locks ORDER BY granted, virtualtransaction;"
            db_query_result = db_connection_obj.connect_to_db(db_query_for_acquired_lock_modes)
            if "error" in db_query_result:
                return db_query_result
            elif db_query_result == []:
                result["Acquired Locks"] = "No Acquired Locks"
            else:
                result_rows = []
                for row in db_query_result:
                    r = self.make_result_for_lock_modes(row)
                    result_rows.append(r)
                result["Modes of Acquired Locks"] = result_rows
            return result

    def get_db_parameters(self):
        pgconnpram = {}
        output = subprocess.check_output('eval `camp-db-params -e`;', shell=True)
        params = str(subprocess.check_output('echo `camp-db-params`', shell=True))
        if params is None or params == "\n":
            try:
                parameters = self.get_db_parameters_using_env()
            except DBParameterNotFoundException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
        else:
            try:
                params = ast.literal_eval(params)
            except ValueError as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if "dbname" not in params:
                raise DBParameterNotFoundException(msg = "dbname not found in environment variable")
            else:
                pgconnpram["dbconnname"] = params["dbname"]
            if "user" not in params:
                raise DBParameterNotFoundException("user not found in environment variable")
            else:
                pgconnpram["dbconnuser"] = params["user"]
            if "host" not in params:
                raise DBParameterNotFoundException("host not found in environment variable")
            else:
                pgconnpram["dbendpoint"] = params["host"]
            if "password" not in params:
                raise DBParameterNotFoundException("password not found in environment variable")
            else:
                pgconnpram["dbconnpass"] = params["password"]
            pgconnpram["dbconnport"] = self.db_connection_port
        return pgconnpram

    def get_db_parameters_using_env(self):
        pgconnpram = {}
        osenv = os.environ
        if osenv is None:
            raise DBParameterNotFoundException("camp-db-params not present in env. variables")
        else:
            if "PGDATABASE" not in osenv:
                raise DBParameterNotFoundException("PGDATABASE not found in environment variable")
            else:
                pgconnpram["dbconnname"] = osenv["PGDATABASE"]
            if "PGUSER" not in osenv:
                raise DBParameterNotFoundException("PGUSER not found in environment variable")
            else:
                pgconnpram["dbconnuser"] = osenv["PGUSER"]
            if "PGHOST" not in osenv:
                raise DBParameterNotFoundException("PGHOST not found in environment variable")
            else:
                pgconnpram["dbendpoint"] = osenv["PGHOST"]
            if "PGPASSWORD" not in osenv:
                raise DBParameterNotFoundException("PGPASSWORD not found in environment variable")
            else:
                pgconnpram["dbconnpass"] = osenv["PGPASSWORD"]
            pgconnpram["dbconnport"] = self.db_connection_port
        return pgconnpram
    
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
