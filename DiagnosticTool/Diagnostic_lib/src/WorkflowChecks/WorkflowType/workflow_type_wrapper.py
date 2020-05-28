activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

from workflow_type import WorkflowType
import sys
import json


#function to invoke from salt
def workflow_type_caller(*argv):
    if len(argv) < 5:
        return {"error": "Invalid parameters paased to salt"}
    instance_name = argv[3]
    workflow_name = argv[4]
    workflow_type_obj = WorkflowType(instance_name, workflow_name)
    workflow_type = {}
    output = workflow_type_obj.get_workflow_type()
    workflow_type["Workflow Type Result"] = output
    workflow_type = json.dumps(workflow_type)
    return workflow_type

'''
#Whenever want to run standalone script
def workflow_type_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 3:
        error_message = dict()
        error_message["error"] = "Campaign Host and workflow name needed as a parameter"
        return error_message
    workflow_type_obj = WorkflowType(args[1], args[2])
    workflow_type = {}
    output = workflow_type_obj.get_workflow_type()
    workflow_type["Workflow Type Result"] = output
    workflow_type = json.dumps(workflow_type)
    print("Final result")
    print(workflow_type)
    return workflow_type

if __name__ == "__main__":
    workflow_type_caller()
'''
