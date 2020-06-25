activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

from DatabaseChecks.IdleAndRunningState.idle_and_running_state import IdleRunningState
import sys
import json

#function to invoke from salt
def idle_and_running_state_caller(*argv):
    if len(argv) != 4:
        return {"error": "Invalid parameters passed to salt"}
    instance_name = argv[3]
    idle_and_running_state_obj = IdleRunningState(instance_name)
    idle_and_running_state = {}
    output = idle_and_running_state_obj.get_running_queries()
    idle_and_running_state["Running Query Result"] = output
    output = idle_and_running_state_obj.get_idle_queries()
    idle_and_running_state["Idle Query Result"] = output
    idle_and_running_state = json.dumps(idle_and_running_state)
    return idle_and_running_state

'''
#Whenever want to run standalone script
def idle_and_running_state_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 2:
        error_message = dict()
        error_message["error"] = "Campaign Host needed as a parameter"
        return error_message
    idle_and_running_state_obj = IdleRunningState(args[1])
    idle_and_running_state = {}
    output = idle_and_running_state_obj.get_running_queries()
    idle_and_running_state["Running Query Result"] = output
    output = idle_and_running_state_obj.get_idle_queries()
    idle_and_running_state["Idle Query Result"] = output
    idle_and_running_state = json.dumps(idle_and_running_state)
    print("Final result")
    print(idle_and_running_state)
    return idle_and_running_state

if __name__ == "__main__":
    idle_and_running_state_caller()
'''
