activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

from WorkflowChecks.WorkflowStatus.workflow_status import WorkflowStatus
import sys
import json

#function to invoke from salt
def workflow_status_caller(*argv):
    if len(argv) < 6:
        return {"error": "Invalid parameters passed to salt"}
    instance_name = argv[3]
    build = argv[4]
    workflow_internalname = argv[5]
    workflow_status_obj = WorkflowStatus(instance_name, build, workflow_internalname)
    workflow_status = {}
    output = workflow_status_obj.get_workflow_status()
    workflow_status["Workflow Status"] = output
    workflow_status = json.dumps(workflow_status)
    return workflow_status

'''
#Whenever want to run standalone script
def workflow_status_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 3:
        error_message = dict()
        error_message["error"] = "Campaign Host needed as a parameter"
        return error_message
    workflow_status_obj = WorkflowStatus(args[1], args[2])
    workflow_status = {}
    output = workflow_status_obj.get_workflow_status()
    workflow_status["Workflow Status"] = output
    workflow_status = json.dumps(workflow_status)
    print("Final result")
    print(workflow_status)
    return workflow_status

if __name__ == "__main__":
    workflow_status_caller()
'''
