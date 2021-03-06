activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

import subprocess
import logging

class WorkflowDailyService:

    def __init__(self, campaign_host):
        self.campaign_host = campaign_host

    def get_workflow_daily_service(self):
        """
        Getting daily workflow status using subprocess module
        """
        result = {}
        try:
            proc1 = subprocess.Popen('su -l -c ". /usr/local/neolane/nl?/env.sh; nlserver pdump -full | grep -A 9 wfserver" neolane', shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = proc1.communicate()
            output, err = str(output), str(err)
            proc1.stdout.close()
            result = self.make_result(output)
            return result
        except subprocess.CalledProcessError as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
        
    def make_result(self, output):
        """
        Making result to return
        """
        result = {}
        lines = output.split("\n")
        for line in lines:
            res = line.split("Start date")
            if len(res)>1 and int(res[1].split('(')[1].split('h')[0])<48: #to check if workflow ran in last 48 hours
                result['Daily Workflow Status'] = "Last Run " + str(res[1].split('(')[1].split(')')[0])
                return result
        result['Daily Workflow Status'] = "Workflow didn't start"
        return result
