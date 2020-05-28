activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

from DatabaseChecks.BloatingAndAnalyze.bloating_and_analyze import BloatingAnalyze
import sys
import json

#function to invoke from salt
def bloating_and_analyze_caller(*argv):
    if len(argv) < 4:
        return {"error": "Invalid parameters paased to salt"}
    instance_name = argv[3]
    bloating_and_analyze_obj = BloatingAnalyze(instance_name)
    bloating_and_analyze = {}
    output = bloating_and_analyze_obj.get_bloating()
    bloating_and_analyze["Bloating Result"] = output
    output = bloating_and_analyze_obj.get_query_analysis()
    bloating_and_analyze["DB Analysis"] = output
    bloating_and_analyze = json.dumps(bloating_and_analyze)
    return bloating_and_analyze

'''
#Whenever want to run standalone script
def bloating_and_analyze_caller():
    print(sys.argv)
    args = sys.argv
    if len(args) != 2:
        error_message = dict()
        error_message["error"] = "Campaign Host needed as a parameter"
        return error_message
    bloating_and_analyze_obj = BloatingAnalyze(args[1])
    bloating_and_analyze = {}
    output = bloating_and_analyze_obj.get_bloating()
    bloating_and_analyze["Bloating Result"] = output
    output = bloating_and_analyze_obj.get_query_analysis()
    bloating_and_analyze["DB Analysis"] = output
    bloating_and_analyze = json.dumps(bloating_and_analyze)
    print("Final result")
    print(bloating_and_analyze)
    return bloating_and_analyze

if __name__ == "__main__":
    bloating_and_analyze_caller()
'''
