activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

from workflow_count_and_state import WorkflowCountAndWebState
import sys
import json

#function to invoke from salt
def workflow_count_and_state_caller(*argv):
    if len(argv) < 4:
        return {"error": "Invalid parameters passed to salt"}
    instance_name = argv[3]
    workflow_count_and_state_obj = WorkflowCountAndWebState(instance_name)
    workflow_count_and_state = {}
    output = workflow_count_and_state_obj.get_workflow_count()
    workflow_count_and_state["Workflow Count Result"] = output
    web_output = []
    output = workflow_count_and_state_obj.get_web_process_usage()
    web_output.append(output)
    output =  workflow_count_and_state_obj.get_last_restart_of_web()
    web_output.append(output)
    workflow_count_and_state["Web Process Result"] = web_output
    workflow_count_and_state = json.dumps(workflow_count_and_state)
    return workflow_count_and_state

'''
#Whenever want to run standalone script
def workflow_count_and_state_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 2:
        error_message = dict()
        error_message["error"] = "Campaign Host needed as a parameter"
        return error_message
    workflow_count_and_state_obj = WorkflowCountAndWebState(args[1])
    workflow_count_and_state = {}
    output = workflow_count_and_state_obj.get_workflow_count()
    workflow_count_and_state["Workflow Count Result"] = output
    web_output = []
    output = workflow_count_and_state_obj.get_web_process_usage()
    web_output.append(output)
    output =  workflow_count_and_state_obj.get_last_restart_of_web()
    web_output.append(output)
    workflow_count_and_state["Web Process Result"] = web_output
    workflow_count_and_state = json.dumps(workflow_count_and_state)
    print("Final result")
    print(workflow_count_and_state)
    return workflow_count_and_state

if __name__ == "__main__":
    workflow_count_and_state_caller()
'''
