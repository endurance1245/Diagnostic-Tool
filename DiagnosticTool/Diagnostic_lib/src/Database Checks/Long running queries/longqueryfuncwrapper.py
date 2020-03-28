#!/usr/bin/python
import longrunningquery

def callablefunc(campaignhost, campaigninstance):
    longrunningqueryresult=longrunningquery.LongQuery(campaignhost, campaigninstance).connecttonewrelic()
    if not bool(longrunningqueryresult):
        #print("Please check if any postgres query is running for more than 5 minutes")
        return "Please check if any postgres query is running for more than 5 minutes"
    elif longrunningqueryresult['Final result'] == 'Unable to connect to database':
        #print("Unable to connect to database due to /Wrong DB name/DB-Table name doesn't exist")
        return "Unable to connect to database due to /Wrong DB name/DB-Table name doesn't exist"
    elif longrunningqueryresult['Final result'] == 'UndefinedTable':
        #print("Unidentified table doesn't exist")
        return "Unidentified table doesn't exist or can be an issue in your query"
    elif longrunningqueryresult['Final result'] == 'Error while fetching from PostgreSQL':
        #print("Error while fetching from PostgreSQL")
        return "Error while fetching from PostgreSQL"
    else:
        #print(longrunningqueryresult)
        return longrunningqueryresult

'''
#To test function locally:-
def main():
    prams = len(sys.argv)
    if prams == 3:
        campaignhost = sys.argv[1]
        campaigninstance = sys.argv[2]
        callablefunc(campaignhost, campaigninstance)
    else:
        print("Parameters passed are incorrect")
if __name__=="__main__":
    main()
'''
