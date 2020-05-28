activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

from boto3 import session
from botocore.config import Config

class AWSBaseConnection(object):

    def __init__(self, resource, region, session_token, max_retries, connect_timeout):
        self.resource = resource
        self.region = region
        self.session_token = session_token
        self.max_retries = max_retries
        self.connect_timeout = connect_timeout
        self.config = self._get_config()
        self.client = self._get_client()

    def _get_client(self):
        s = session.Session(aws_session_token=self.session_token, region_name=self.region)
        client = s.client(self.resource, config=self.config)
        return client

    def _get_config(self):
        config = Config(
            retries=dict(
                max_attempts = self.max_retries
            ),
            connect_timeout = self.connect_timeout
        )
        return config
