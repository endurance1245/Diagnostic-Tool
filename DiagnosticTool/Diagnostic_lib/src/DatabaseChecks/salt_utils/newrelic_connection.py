from nrql.api import NRQL
from database_exceptions import BadRequestException

class NewRelicInsight:

    def __init__(self, campaignhost, log):

        self.campaignhost = campaignhost
        self.log = log
        self.nrql = NRQL()
        self.nrql.api_key = ''   #to be added once configured in vault
        self.nrql.account_id = '' #to be added once configured in vault
        self.result = None

    def fetch_result_from_newrelic(self, query):
        try:
            self.result = self.nrql.query(query)
        except Exception as err:
            self.log.error(err)
            raise BadRequestException("Incorrect API key/account id/query for NewRelic")
        return self.result
