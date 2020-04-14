from nrql.api import NRQL

class NewRelicInsight:

    def __init__(self, campaignhost, log, query):

        self.campaignhost = campaignhost
        self.query = query
        self.log = log
        self.nrql = NRQL()
        self.nrql.api_key = 'NRIQ-11mEyoS61grbFtI4hPNVIH-G0ihSS-Nt'
        self.nrql.account_id = '1209327'
        self.result = None

    def fetch_result_from_newrelic(self):
        try:
            self.result = self.nrql.query(self.query)
        except Exception as err:
            #Below is applicable for incorrect API key/account id/incorrect newrelic query
            self.log.error(err)
            error_message = dict()
            error_message['error'] = str(err)
            return error_message
        return self.result
