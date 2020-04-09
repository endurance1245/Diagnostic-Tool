#!/usr/bin/python
from DatabaseChecks.LongRunningQueries.longrunningquery import LongQuery
import sys
import logging

def callablefunc(campaignhost, campaigninstance):
    longrunningqueryresult=LongQuery(campaignhost, campaigninstance).connecttonewrelic()
    if not bool(longrunningqueryresult):
        print("Please check if any postgres query is running for more than 5 minutes")
        return "Please check if any postgres query is running for more than 5 minutes"

    elif longrunningqueryresult['Final result'] == 'Unable to connect to database':
        print("Unable to connect to database due to /Wrong DB name/DB-Table name doesn't exist")
        return "Unable to connect to database due to /Wrong DB name/DB-Table name doesn't exist"

    elif longrunningqueryresult['Final result'] == "It seems neither camp-db-params nor the environment variable for database is set":
        print("It seems neither camp-db-params nor the environment variable for database is set")
        return "It seems neither camp-db-params nor the environment variable for database is set"

    elif longrunningqueryresult['Final result'] == 'UndefinedTable':
        print("Unidentified table doesn't exist")
        return "Unidentified table doesn't exist or can be an issue in your query"

    elif longrunningqueryresult['Final result'] == 'Error while fetching from PostgreSQL':
        print("Error while fetching from PostgreSQL")
        return "Error while fetching from PostgreSQL"

    elif longrunningqueryresult['Final result'] == "Please check as why there is no long query running during this point on the server":
        print("Please check as why there is no long query running during this point on the server")
        return "Please check as why there is no long query running during this point on the server"

    elif longrunningqueryresult['Final result'] == "It seems newrelic doesn't have any data since an hour, please check if something is wrong e.g. newrelic agent stopped on DB machine":
        print("It seems newrelic doesn't have any data since an hour, please check if something is wrong e.g. newrelic agent stopped on DB machine")
        return "It seems newrelic doesn't have any data since an hour, please check if something is wrong e.g. newrelic agent stopped on DB machine"

    elif longrunningqueryresult['Final result'] == "It seems the API/account details for connecting to newrelic are incorrect":
        print("It seems the API/account details for connecting to newrelic are incorrect")
        return "It seems the API/account details for connecting to newrelic are incorrect"

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
