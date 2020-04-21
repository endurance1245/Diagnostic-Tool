from blocking_and_deadlock import BlockingDeadlock
import sys
import json

#function to invoke from salt
def blocking_and_deadlock_caller(*argv):
    if argv.len != 4:
        return {"error": "Invalid parameters paased to salt"}
    instance_name = argv[3]
    blocking_and_deadlock_obj = BlockingDeadlock(instance_name)
    blocking_and_deadlock = {}
    output = blocking_and_deadlock_obj.get_blocking_queries()
    blocking_and_deadlock["Blocking Result"] = output
    output = blocking_and_deadlock_obj.get_deadlock_queries()
    blocking_and_deadlock["Deadlock Result"] = output
    blocking_and_deadlock = json.dumps(blocking_and_deadlock)
    return blocking_and_deadlock


'''
#Whenever want to run standalone script
def blocking_and_deadlock_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 2:
        error_message = dict()
        error_message["error"] = "Campaign Host needed as a parameter"
        return error_message
    blocking_and_deadlock_obj = BlockingDeadlock(args[1])
    blocking_and_deadlock = {}
    output = blocking_and_deadlock_obj.get_blocking_queries()
    blocking_and_deadlock["Blocking Result"] = output
    output = blocking_and_deadlock_obj.get_deadlock_queries()
    blocking_and_deadlock["Deadlock Result"] = output
    blocking_and_deadlock = json.dumps(blocking_and_deadlock)
    print("Final result")
    print(blocking_and_deadlock)
    return blocking_and_deadlock

if __name__ == "__main__":
    blocking_and_deadlock_caller()
'''
