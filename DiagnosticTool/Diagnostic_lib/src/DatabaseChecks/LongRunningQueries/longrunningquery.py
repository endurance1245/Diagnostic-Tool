#!/usr/bin/python
import os
import pgconnection
import newrelicconnection
import logging


class LongQuery():
    def __init__(self,campaignhost,campaigninstance):
        self.campaignhost=campaignhost
        self.campaigninstance=campaigninstance

        #API to query inventory
        self.api_key='c1fda300-2a62-4221-8036-0082edbdab4f'
        self.url = "https://us-east-1-483013340174-inventory-dev.camp-infra.adobe.net/instances/"+self.campaigninstance

        #Dict to save details of credentials to connect to database
        self.pgconnpram = {}

        # DB port details
        self.dbconnport = 5432

        #Final result
        self.longrunquery={}

    def connecttonewrelic(self):
        self.longqueryexist=newrelicconnection.NewRelic(self.campaignhost).newrelicfetchinfo()
        if self.longqueryexist['longqueryexist'] == True:
            return self.fetchdbname_usingeval()
        elif self.longqueryexist['longqueryexist'] == False:
            self.longrunquery['Final result'] = "Please check as why there is no long query running during this point on the server"
            return self.longrunquery
        elif self.longqueryexist['longqueryexist'] == 'unknown':
            self.longrunquery['Final result'] = "It seems newrelic doesn't have any data since an hour, please check if something is wrong e.g. newrelic agent stopped on DB machine"
            return self.longrunquery
        elif self.longqueryexist['longqueryexist'] == 'incorrectapidetails':
            self.longrunquery['Final result'] = "It seems the API/account details for connecting to newrelic are incorrect"
            return self.longrunquery

    def fetchdbname_usingeval(self):
        self.runenv=os.popen('eval `camp-db-params -e`;')
        self.fetchenv=os.popen('echo `camp-db-params`').read()

        #To convert a string to a dict apart from json.loads
        self.fetchenv=eval(self.fetchenv)

        if not bool(self.fetchenv):
            #return "It seems the camp-db-params for database isn't set"
            #CASE 2 Try to fetch details via environment variables
            return self.fetchdbname_usingenv()
        else:
            # Setting DB credentials for connection
            self.pgconnpram['dbconnname'] = self.fetchenv['dbname']
            self.pgconnpram['dbconnuser'] = self.fetchenv['user']
            self.pgconnpram['dbendpoint'] = self.fetchenv['host']
            self.pgconnpram['dbconnpass'] = self.fetchenv['password']
            self.pgconnpram['dbconnport'] = str(self.dbconnport)
            return self.connecttodb()

    def fetchdbname_usingenv(self):
        self.osenv = os.environ
        if not bool(self.osenv):
            return "It seems neither camp-db-params nor the environment variable for database is set"

            #CASE 3 try to fetch DB info using inventory and password using vault, code to be written
        else:
            # Setting DB credentials for connection
            self.pgconnpram['dbconnname'] = self.osenv['PGDATABASE']
            self.pgconnpram['dbconnuser'] = self.osenv['PGUSER']
            self.pgconnpram['dbendpoint'] = self.osenv['PGHOST']
            self.pgconnpram['dbconnpass'] = self.osenv['PGPASSWORD']
            self.pgconnpram['dbconnport'] = str(self.dbconnport)
            return self.connecttodb()

    def connecttodb(self):
        self.longrunquery['Final result'] = pgconnection.PgConnection(logging, self.pgconnpram).longrunningquery()
        return self.longrunquery

