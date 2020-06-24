activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

from WorkflowChecks.WorkflowDailyService.workflow_daily_service import WorkflowDailyService
import sys
import json

#function to invoke from salt
def workflow_daily_service_caller(*argv):
    if len(argv) < 4:
        return {"error": "Invalid parameters passed to salt"}
    instance_name = argv[3]
    workflow_daily_service_obj = WorkflowDailyService(instance_name)
    workflow_daily_service = {}
    output = workflow_daily_service_obj.get_workflow_daily_service()
    workflow_daily_service["Workflow Daily Service"] = output
    workflow_daily_service = json.dumps(workflow_daily_service)
    return workflow_daily_service

'''
#Whenever want to run standalone script
def workflow_daily_service_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 2:
        error_message = dict()
        error_message["error"] = "Campaign Host needed as a parameter"
        return error_message
    workflow_daily_service_obj = WorkflowDailyService(args[1])
    workflow_daily_service = {}
    output = workflow_daily_service_obj.get_workflow_daily_service()
    workflow_daily_service["Workflow Daily Service"] = output
    workflow_daily_service = json.dumps(workflow_daily_service)
    print("Final result")
    print(workflow_daily_service)
    return workflow_daily_service

if __name__ == "__main__":
    workflow_daily_service_caller()
'''
