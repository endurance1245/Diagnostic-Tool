activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

import logging
from campaign_db_connection import PgConnection
from db_parameters import DbParameters
from database_exceptions import DBParameterNotFoundException, DataBaseException

class WorkflowType:

    def __init__(self, campaign_host, workflow_name):
        self.campaign_host = campaign_host
        self.workflow_name = workflow_name

    def check_workflow_existence(self):
        params = self.get_db_params()
        if "error" in params:
            return params
        else:
            result = []
            db_connection_obj = PgConnection(logging, params)
            try:
                db_query_for_workflow_id = "select iworkflowid, sinternalname, slabel from xtkworkflow where sinternalname LIKE '%{}%';"
                db_query_result = db_connection_obj.get_result_from_db(db_query_for_workflow_id.format(self.workflow_name))
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            if db_query_result == []:
                return False
            return True

    def get_workflow_type(self):
        result = dict()
        technical_workflow_list = ['reportingAggregates', 'billing', 'aliasCleansing', 'deliverabilityUpdate',
        'cleanup', 'offerMgt', 'forecasting', 'tracking', 'billingActiveContactCount',
        'budgetMgt', 'stockMgt', 'deliveryMgt', 'operationMgt', 'supplierMgt',
        'assetMgt', 'taskMgt', 'newsgroupMgt', 'agg_nmspropositionrcp_full', 'cleanup',
        'statsFacebook', 'syncFacebookFans', 'syncFacebook', 'statsTwitter', 'syncTwitter',
        'synchLaunch', 'eventSynch', 'broadLogMsgSynch', 'broadLogSynch', 'trackingUrlSynch',
        'trackingLogSynch', 'quarantineSynch', 'updateEventsStatus', 'batchEventsProcessing', 
        'rtEventsProcessing', 'mobileAppOptOutMgt', 'webAnalyticsSendMetrics', 'webAnalyticsFindConverted',
        'webAnalyticsPurgeWebEvents', 'webAnalyticsGetWebEvents', 'updateRenderingSeeds',
        'defaultMidSourcingDlv', 'defaultMidSourcingLog', 'deliveryIndicators']
        workflow_existence = self.check_workflow_existence()
        if type(workflow_existence) is not bool:
            return workflow_existence
        if workflow_existence:
            if self.workflow_name in technical_workflow_list:
                result["workflow type"] = "Technical Workflow"
            else:
                result["workflow type"] = "Custom"
        else:
            result["error"] = "Workflow with this name doesn't exist for " + self.campaign_host
        result["workflow name"] = self.workflow_name
        return result

    def get_db_params(self):
        try:
            params_obj = DbParameters()
            params = params_obj.get_db_parameters()
            return params
        except DBParameterNotFoundException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message


