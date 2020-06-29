from WorkflowChecks.WorkflowTablesKeepinterminflag.workflow_tables_keepinterminflag import WorkflowTablesKeepinterminflag
import sys
import json

#function to invoke from salt
def workflow_tablekeepresult_caller(*argv):
    if len(argv) < 6:
        return {"error": "Invalid parameters passed to salt"}
    instance_name = argv[3]
    build = argv[4]
    workflow_internalname = argv[5]
    workflow_obj = WorkflowTablesKeepinterminflag(instance_name, build, workflow_internalname)
    workflow_tables_keepresultflag = {}
    output = workflow_obj.get_workflow_keepresultflag()
    workflow_tables_keepresultflag["Keep Result Flag"] = output
    output = workflow_obj.get_workflow_tables()
    workflow_tables_keepresultflag["Tables"] = output
    workflow_tables_keepresultflag = json.dumps(workflow_tables_keepresultflag)
    return workflow_tables_keepresultflag


'''
#Whenever want to run standalone script
def workflow_tablekeepresult_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 4:
        error_message = dict()
        error_message["error"] = "Campaign Host needed as a parameter"
        return error_message
    workflow_obj = WorkflowTablesKeepinterminflag(args[1], args[2], arg[3])
    workflow_tables_keepresultflag = {}
    output = workflow_obj.get_workflow_keepresultflag()
    workflow_tables_keepresultflag["Keep Result Flag"] = output
    output = workflow_obj.get_workflow_tables()
    workflow_tables_keepresultflag["Tables"] = output
    workflow_tables_keepresultflag = json.dumps(workflow_tables_keepresultflag)
    print("Final result")
    print(workflow_tables_keepresultflag)
    return workflow_tables_keepresultflag

if __name__ == "__main__":
    workflow_tablekeepresult_caller()
'''
