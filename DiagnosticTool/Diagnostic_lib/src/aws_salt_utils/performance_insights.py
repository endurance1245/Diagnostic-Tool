activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))
        
from datetime import datetime, timedelta
import json
import logging
from aws_connection import AWSBaseConnection
from rds_connection  import RDSConnection
from aws_constants import BOTO_CONNECT_TIMEOUT, BOTO_MAX_RETRIES
from aws_exceptions import RDSClientException, RDSConnectionException, ResourceIdNotFoundException, PerformanceInsightsConnectionException

class PerformanceInsights(AWSBaseConnection):
    def __init__(self, region, session_token=None,
                 max_retries=BOTO_MAX_RETRIES, connect_timeout=BOTO_CONNECT_TIMEOUT):
        AWSBaseConnection.__init__(self, resource='pi', region=region, session_token=session_token, max_retries=max_retries,
                                   connect_timeout=connect_timeout)

    def get_pi_resource_metrices(self, metric_queries, campaign_db_name, start_time, end_time):
        try:
            db_instance_info = RDSConnection(self.region).get_db_instance(campaign_db_name)
        except RDSClientException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        except RDSConnectionException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        except Exception as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        if 'DBInstances' in db_instance_info and 'DbiResourceId' in db_instance_info['DBInstances'][0]:
            resource_id = db_instance_info['DBInstances'][0]['DbiResourceId']
        else:
            raise ResourceIdNotFoundException("Resource id isn't available for db " + campaign_db_name)
        try:
            response = self.client.get_resource_metrics(
                    ServiceType='RDS',
                    Identifier=resource_id,
                    MetricQueries = metric_queries,
                    StartTime=start_time,
                    EndTime=end_time,
                    PeriodInSeconds=3600,
                    MaxResults=10
            )
        except Exception as err:
            logging.error(str(err))
            raise PerformanceInsightsConnectionException(str(err))
        return response
