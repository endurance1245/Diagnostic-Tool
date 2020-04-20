#!/usr/bin/python
from DatabaseChecks.LongRunningQueries.longrunningquery import LongQuery
import sys
import logging
import json

def callablefunc(*argv):
    campaignhost=argv[3]

    longrunningqueryresult = LongQuery(campaignhost).connecttonewrelic()
    if not bool(longrunningqueryresult):
        print("Please check if any postgres query is running for more than 5 minutes")
        return json.dumps({"Final result":"Please check if any postgres query is running for more than 5 minutes"})

    elif longrunningqueryresult['Final result'] == 'Unable to connect to database':
        print("Unable to connect to database due to /Wrong DB name/DB-Table name doesn't exist")
        return json.dumps({"Final result": "Unable to connect to database due to /Wrong DB name/DB-Table name doesn't exist"})

    elif longrunningqueryresult['Final result'] == "It seems neither camp-db-params nor the environment variable for database is set":
        print("It seems neither camp-db-params nor the environment variable for database is set")
        return json.dumps({"Final result": "It seems neither camp-db-params nor the environment variable for database is set"})

    elif longrunningqueryresult['Final result'] == 'UndefinedTable':
        print("Unidentified table doesn't exist")
        return json.dumps({"Final result": "Unidentified table doesn't exist or can be an issue in your query"})

    elif longrunningqueryresult['Final result'] == 'Error while fetching from PostgreSQL':
        print("Error while fetching from PostgreSQL")
        return json.dumps({"Final result": "Error while fetching from PostgreSQL"})

    elif longrunningqueryresult['Final result'] == "Please check as why there is no long query running during this point on the server":
        print("Please check as why there is no long query running during this point on the server")
        return json.dumps({"Final result": "Please check as why there is no long query running during this point on the server"})

    elif longrunningqueryresult['Final result'] == "It seems newrelic doesn't have any data since an hour, please check if something is wrong e.g. newrelic agent stopped on DB machine":
        print("It seems newrelic doesn't have any data since an hour, please check if something is wrong e.g. newrelic agent stopped on DB machine")
        return json.dumps({"Final result": "It seems newrelic doesn't have any data since an hour, please check if something is wrong e.g. newrelic agent stopped on DB machine"})

    elif longrunningqueryresult['Final result'] == "It seems the API/account details for connecting to newrelic are incorrect":
        print("It seems the API/account details for connecting to newrelic are incorrect")
        return json.dumps({"Final result": "It seems the API/account details for connecting to newrelic are incorrect"})
    elif longrunningqueryresult['Final result'] == "It seems there's an unknown exception please check newrelic results for long query":
        print("It seems there's an unknown exception please check newrelic results for long query")
        return json.dumps({"Final result": "It seems there's an unknown exception please check newrelic results for long query"})

    else:
        print(longrunningqueryresult)
        return longrunningqueryresult

'''
#To test function locally:-
def main():
    import sys
    prams = len(sys.argv)
    if prams == 3:
        campaignhost = sys.argv[1]
        campaigninstance = sys.argv[2]
        callablefunc(campaignhost, campaigninstance)
    else:
        print("Parameters passed are incorrect")


if __name__ == "__main__":
    main()
'''
