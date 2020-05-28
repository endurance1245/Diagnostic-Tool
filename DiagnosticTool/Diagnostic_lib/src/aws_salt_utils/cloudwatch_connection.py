activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))
        
import logging
from botocore.exceptions import ClientError
from datetime import datetime,  timedelta
from aws_connection import AWSBaseConnection
from aws_constants import BOTO_MAX_RETRIES, BOTO_CONNECT_TIMEOUT
from aws_exceptions import CloudWatchConnectionException

class CloudWatchConnection(AWSBaseConnection):
    def __init__(self, region, session_token=None,
                 max_retries=BOTO_MAX_RETRIES, connect_timeout=BOTO_CONNECT_TIMEOUT):
        AWSBaseConnection.__init__(self, resource='cloudwatch', region=region, session_token=session_token, 
                            max_retries=max_retries, connect_timeout=connect_timeout)

    def get_avg_metric_statistics(self, metric_name, dimension_name, campaign_db_name, start_time, 
                                    end_time, interval):
        try:
            metric_stat = self.client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName= metric_name,
                Dimensions=[
                    {
                        'Name': dimension_name,
                        'Value': campaign_db_name
                    },
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=interval,
                Statistics=[
                    'Average',
                ],
            )
            return metric_stat
        except Exception as err:
            logging.error(err.message)
            raise CloudWatchConnectionException(err.message)
