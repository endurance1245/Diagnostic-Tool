import logging
import json
from campaign_db_connection import PgConnection
from db_parameters import DbParameters
from database_exceptions import DBParameterNotFoundException, DataBaseException
from db_queries import db_query_for_workflow_id, db_query_for_workflow_status

class WorkflowStatus:

    def __init__(self, campaign_host, workflow_internalname):
        self.campaign_host = campaign_host
        self.workflow_internalname = workflow_internalname
    
    def get_workflow_status(self):
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
                db_query_result = db_connection_obj.get_result_from_db(db_query_for_workflow_id.format(self.workflow_internalname))
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result == []:
                result["workflow_id"] = "ID not found"
            else:
                result = []
                for row in db_query_result:
                    r = self.make_result_for_workflow_id(row) #form dictionary from the returned row of db
                    try:
                         db_query_result_status = db_connection_obj.get_result_from_db(db_query_for_workflow_status.format(r["workflow_id"]))
                    except DataBaseException as err:
                        logging.error(err)
                        error_message = dict()
                        error_message["error"] = str(err)
                        return error_message
                    if db_query_result_status == []:
                        r["Status"] = "Not Found"
                        result.append(r)
                    else:
                        for value in db_query_result_status:
                            r.update(self.make_result_for_workflow_status(value))
                            result.append(r)
        return result
    
    def make_result_for_workflow_id(self, row):
        result = {}
        result["workflow_id"] = row[0]
        result["workflow_internallabel"] = row[1]
        result["workflow_label"] = row[2]
        return result

    def make_result_for_workflow_status(self, row):
        result = {}
        result["workflow_pid"] = row[0]
        result["workflow_status"] = row[1]
        result["workflow_duration"] = str(row[3])
        result["workflow_query"] = row[4]
        return result
