import logging

from campaign_db_connection import PgConnection
from db_parameters import DbParameters
from database_exceptions import DBParameterNotFoundException, DataBaseException
from db_queries import  db_query_for_keepinterminflag_in_workflow, db_query_for_keepinterminflag_in_workflow_acs , db_query_for_number_of_tables_in_workflow , db_query_for_number_of_tables_in_workflow_acs

class WorkflowTablesKeepinterminflag:

    def __init__(self, campaign_host , build, workflow_internalname):
        self.campaign_host = campaign_host
        self.build = int(build)
        self.workflow_internalname = workflow_internalname
        
    
    def get_workflow_tables(self):
        try:
            params_obj = DbParameters()
            params = params_obj.get_db_parameters()
        except DBParameterNotFoundException as err:
            logging.error(err)
            error_message = {}
            error_message["error"] = str(err)
            return error_message
        if "error" in params:
            return params
        else:
            result = {}
            db_connection_obj = PgConnection(logging, params)
            try:
                if(self.build < 10000):
                    db_query = db_query_for_number_of_tables_in_workflow
                else:
                    db_query = db_query_for_number_of_tables_in_workflow_acs

                db_query_result_tables = db_connection_obj.get_result_from_db(db_query.format(self.workflow_internalname))
            except DataBaseException as err:
                logging.error(err)
                error_message = {}
                error_message["error"] = str(err)
                return error_message
            if db_query_result_tables == []:
                result["workflow_tables"] = "Currently None"
            else:
                result = []
                for row in db_query_result_tables:
                    r = self.make_result_for_keepflag(row)
                    result.append(r)
                
        return result


    def get_workflow_keepresultflag(self):
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
                if(self.build < 10000):
                    db_query = db_query_for_keepinterminflag_in_workflow
                else:
                    db_query = db_query_for_keepinterminflag_in_workflow_acs

                db_query_result_keepintermin = db_connection_obj.get_result_from_db(db_query.format(self.workflow_internalname))
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result_keepintermin == []:
                result["keepresult_flag"] = "Currently set to false"
            else:
                result ["keepresult_flag"] = "Currently set to True"
                result_rows = []
                for row in db_query_result_keepintermin:
                    r = self.make_result_for_keepflag(row)
                    result_rows.append(r)
                result["workflow_details"] = result_rows
                
        return result
    
    def make_result_for_keepflag(self, row):
        result = {}
        result["workflow_id"] = row[0]
        result["workflow_internalname"] = row[1]
        result["workflow_label"] = row[2]
        return result

    def make_result_for_workflow_tables(self, row):
        result = {}
        result["workflow_workflow_tables"] = row[3]
        result["workflow_label"] = str(row[0])
        result["workflow_internalname"] = row[1]
        return result
