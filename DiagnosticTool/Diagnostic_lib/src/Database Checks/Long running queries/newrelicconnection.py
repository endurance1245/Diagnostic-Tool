#!/usr/bin/python
from nrql.api import NRQL

class newrelic(Exception):
    def __init__(self,campaignhost):

        self.campaignhost=campaignhost
        self.nrql = NRQL()
        self.nrql.api_key = 'NRIQ-11mEyoS61grbFtI4hPNVIH-G0ihSS-Nt'
        self.nrql.account_id = '1209327'
        self.longqueryexist={}

    def newrelicfetchinfo(self):
        queryInsights = "FROM Postgres select average(oldest_query)* 1000  as oldest_query_in_ms where " \
                        "queryName = 'PG_OLDEST_QUERY_AND_TRANSACTION' and hostname " \
                        "like '%" + self.campaignhost + "%' facet hostname TIMESERIES 5 minutes since 5 minutes ago"

        queryInsightsfor1hour = "FROM Postgres select average(oldest_query)* 1000  as oldest_query_in_ms where " \
                                "queryName = 'PG_OLDEST_QUERY_AND_TRANSACTION' and hostname " \
                                "like '%" + self.campaignhost + "%' facet hostname TIMESERIES 5 minutes since 60 minutes ago"

        # Exception handling for incorrect NewRelic API key or account ID
        try:
            self.reqvariable = self.nrql.query(queryInsights)
            self.reqvariablesince1hour = self.nrql.query(queryInsightsfor1hour)
            self.inspectedcountsince1hour = self.reqvariablesince1hour['totalResult']['total']['inspectedCount']
            self.inspectedcount = self.reqvariable['totalResult']['total']['inspectedCount']
            self.longquery = self.reqvariable['facets'][0]['total']['results'][0]['result'] / 1000 ** 2

        except Exception as e:
            #Below is applicable for incorrect API key/account id/incorrect newrelic query , print("Exception", e)
            self.longqueryexist['longqueryexist'] = 'incorrectnewrelicinfo'
            return self.longqueryexist

        #Check how many events are there in last 5 minutes, which must be 5 as newrelic is capturing data every 5minutes as well from postgres.
        #Check for last one hour no of estimated events check for seeing if we are getting data from newrelic.
        if self.inspectedcountsince1hour == 0:
            self.longqueryexist['longqueryexist'] = 'Unknown'
        elif self.inspectedcount >= 1:
            if self.longquery < 0:
                self.longqueryexist['longqueryexist'] = True
            else:
                self.longqueryexist['longqueryexist'] = False
        return self.longqueryexist