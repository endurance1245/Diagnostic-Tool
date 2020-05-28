import subprocess
import logging
import json

def workflow_count():
    result = {}
    workflow_upper_limit = 15
    try:
        p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "runwf"], stdin=p1.stdout, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        p3 = subprocess.Popen(["wc", "-l"], stdin=p2.stdout, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        out, err = p3.communicate()
    except subprocess.CalledProcessError as err:
        logging.error(err)
        result["error"] = str(err)
        return result
    except OSError as err:
        logging.error(err)
        result["error"] = str(err)
        return result
    except Exception as err:
        logging.error(err)
        result["error"] = str(err)
        return result
    output = int(out)
    result["No. of workflows running"]  = output - 1
    result["state"] = "Ok"
    if output - 1 > workflow_upper_limit:
        result["state"] = "Too many workflows running. Try to reduce them or upgrade the package."
    result = json.dumps(result)
    return result
