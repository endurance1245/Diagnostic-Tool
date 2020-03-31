How to run the script using salt module?
root@salt-syndic-1:~# salt 'futureadvisor-rt-prod6-2' longqueryfuncwrapper.callablefunc futureadvisor-rt-prod6-1 futureadvisor_rt_prod6
futureadvisor-rt-prod6-2:
    ----------
    Final result::
        ----------
        2282:
            INSERT INTO XtkWorkflowLog (iWorkflowLogId, iWorkf
        2283:
            INSERT INTO XtkWorkflowLog (iWorkflowLogId, iWorkf

To run the script locally:-
First remove the comments in file longqueryfuncwrapper.py and then run as below:-
root@futureadvisor-rt-prod6-2:/var/cache/salt/minion/extmods/modules# python longqueryfuncwrapper.py futureadvisor-rt-prod6-1 futureadvisor_rt_prod6
{2282: 'INSERT INTO XtkWorkflowLog (iWorkflowLogId, iWorkf', 2283: 'INSERT INTO XtkWorkflowLog (iWorkflowLogId, iWorkf'}

Script flow:-
longrunningqueryresult=longrunningquery.longquery(campaignhost, campaigninstance).connecttonewrelic()
Above script would be called first, where we pass campaign host and instance to longquery class and method connecttonewrelic(). Next after reaching longrunningquery file we see code self.longqueryexist=newrelicconnection.newrelic(self.campaignhost).newrelicfetchinfo() where we will fetch info from newrelic that whether any long running query exists or not for last 5 mins. Once long query is identified we proceed to code self.fetchdbname_usingeval(). Here we fetch env parameters for connecting to database, post getting the creds we call self.connecttodb(), and we connect to db and fetch query details using  pgconnection.Pgconnection(logging, self.pgconnpram).longrunningquery(). The query to fetch long running from postgres would fetch any query which is running > 5mins and isn't idle and then would return the output with PID.
