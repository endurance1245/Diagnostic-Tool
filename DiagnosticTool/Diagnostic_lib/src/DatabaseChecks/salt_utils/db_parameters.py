activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))
        
import ast
import subprocess
import logging
import os
from database_exceptions import DBParameterNotFoundException

class DbParameters:
    def __init__(self):
        self.db_connection_port = "5432"

    def get_db_parameters(self):
        pgconnpram = {}
        output = subprocess.check_output('eval `camp-db-params -e`;', shell=True)
        params = str(subprocess.check_output('echo `camp-db-params`', shell=True),'utf-8')
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
                raise DBParameterNotFoundException("dbname not found in environment variable")
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
