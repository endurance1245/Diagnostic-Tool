activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

import logging
from botocore.exceptions import ClientError
from aws_connection import AWSBaseConnection
from aws_constants import BOTO_MAX_RETRIES, BOTO_CONNECT_TIMEOUT
from aws_exceptions import RDSClientException, RDSConnectionException

class RDSConnection(AWSBaseConnection):
    def __init__(self, region, session_token=None,
                 max_retries=BOTO_MAX_RETRIES, connect_timeout=BOTO_CONNECT_TIMEOUT):
        AWSBaseConnection.__init__(self, resource='rds', region=region, session_token=session_token, 
                            max_retries=max_retries, connect_timeout=connect_timeout)

    def get_db_instance(self, campaign_db_name):
        try:
            db_instance_info = self.client.describe_db_instances(
                DBInstanceIdentifier = campaign_db_name,
                MaxRecords=20
            )
            return db_instance_info
        except ClientError as err:
            logging.error(err.message)
            raise RDSClientException(err.message)
        except Exception as err:
            logging.error(err.message)
            raise RDSConnectionException(err.message)
    
