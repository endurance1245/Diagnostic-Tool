#!/usr/bin/python
import longrunningquery
import sys

def callablefunc(campaignhost, campaigninstance):
    longrunningqueryresult=longrunningquery.longquery(campaignhost, campaigninstance).connecttonewrelic()
    if not bool(longrunningqueryresult):
        return "Please check if any postgres query is running for more than 5 minutes"
    else:
        return longrunningqueryresult

#To test function locally:-
'''
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