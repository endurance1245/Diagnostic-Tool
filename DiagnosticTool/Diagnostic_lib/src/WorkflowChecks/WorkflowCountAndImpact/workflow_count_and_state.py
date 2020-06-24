activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

import subprocess
import logging
import os
import xml.etree.ElementTree as ET

class WorkflowCountAndWebState:
    
    def __init__(self, campaign_host):
        self.campaign_host = campaign_host

    def get_workflow_count(self):
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
        return result
    
    def get_web_process_usage(self):
        result = {}
        try:
            web_process = str(subprocess.check_output('nlserver pdump | grep web@default', shell=True))
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
        web_memory  = web_process.split("- ")[-1]
        web_memory = web_memory.split("\n")[0]
        result["Web process usage"] =  web_memory
        return result

    def get_last_restart_of_web(self):
        result = {}
        try:
            p1 = subprocess.Popen(["nlserver", "monitor"], stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
            p2 = subprocess.Popen(["grep", "-A3", "web"], stdin=p1.stdout, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
            out, err = p2.communicate()
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
        process_root = ET.fromstring(out)
        if "dead" in process_root.attrib:
            process_dead_state = process_root.attrib["dead"]
        else:
            process_dead_state = "true"
        if "lastAlive" in process_root.attrib:
            process_last_restart = str(process_root.attrib["lastAlive"])
        else:
            process_last_restart = "last restart time of web process isn't present"
        if "restartDate" in process_root.attrib:
            process_next_restart = str(process_root.attrib["restartDate"])
        else:
            process_next_restart = "next restart time of web process isn't present"
        if process_dead_state == "false":
            process_state = "web process is running fine"
        else:
            process_state = "web process isn't running"
        result["web process state"] = process_state
        result["last restart time of web process"] = process_last_restart
        result["next scheduled restart of web process"] = process_next_restart
        return result
