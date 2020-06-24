import os
import psutil
import subprocess
import json

#Memory usage
def get_memory_usage(*argv):
    result = {}
    mem = dict(psutil.virtual_memory()._asdict())
    used_memory = mem["used"] / (1024*1024) #In MB
    total_memory = mem["total"] / (1024*1024) #In MB
    memory_utilization = (used_memory/float(total_memory)) * 100
    memory_utilization = round(memory_utilization, 2)
    state = ""
    if memory_utilization <= 80:
        state = "Ok(Memory Usage)"
    elif memory_utilization > 80 and memory_utilization <= 90:
        state = "Warning(Memory Usage)"
    else:
        state = "Critical(Memory Usage)"
    result["memory_utilization"] = memory_utilization
    result["state"] = state
    result = json.dumps(result)
    return result

#swap memory information
def get_swap_memory_usage(*argv):
    #print(psutil.swap_memory())
    result = {}
    used_swap = psutil.swap_memory()[1]
    total_swap = psutil.swap_memory()[0]
    if total_swap == 0:
        swap_utilization = 0.00
        state = "Swap not configured"
    else :
        swap_utilization = (used_swap/float(total_swap)) * 100
        swap_utilization = round(swap_utilization, 2)
        if swap_utilization <= 40:
            state = "Ok(Swap Usage)"
        elif swap_utilization > 40 and swap_utilization <= 50:
            state = "Warning(Swap Usage)"
        else:
            state = "Critical(Swap Usage)"
    result["swap_utilization"] = swap_utilization
    result["state"] = state
    result = json.dumps(result)
    return result

def get_mta_usage(*argv):
    #Find mta process id
    result = {}
    try:
        mta_process = str(subprocess.check_output('nlserver pdump | grep mta', shell=True))
    except subprocess.CalledProcessError as e:
        result["message"] = "MTA not running"
        result = json.dumps(result)
        return result
    pid_start_index = mta_process.find("(")
    pid_end_index = mta_process.find(")")
    pid = mta_process[pid_start_index+1 : pid_end_index]
    #print(pid)
    #MTA information
    p = psutil.Process(int(pid))
    #print(p.memory_info())  
    used_mta = p.memory_info().rss
    print("memory used by mta in MB - " , used_mta / (1024*1024)) 
    result["memory_used_by_mta"] = used_mta / (1024*1024)
    result = json.dumps(result)
    return result

def get_load_average(*argv):
    result = {}
    #load average
    load_avg = os.getloadavg() 
    one_minute_load_avg = load_avg[0]
    no_of_cpu_cores = psutil.cpu_count()
    utilization = (one_minute_load_avg/float(no_of_cpu_cores)) * 100
    utilization = round(utilization, 2)
    state = ""
    if utilization <= 80.00:
        state = "Ok(CPU Utilization)"
    elif utilization>80.00 and utilization<=90.00:
        state = "Warning(CPU Utilization)"
    else:
        state = "Critical(CPU Utilization)"
    result["load_average_15"] = load_avg[2]
    result["cpu_utilization"] = utilization
    result["state"] = state
    result = json.dumps(result)
    return result
    
def get_number_of_pids(*argv):
    result = {}
    try:
        number_of_pids = int(subprocess.check_output('ps -ef | wc -l', shell=True))
    except subprocess.CalledProcessError as err:
        result["error"] = str(err)
        result = json.dumps(result)
        return result
    if number_of_pids <= 2:
        number_of_pids = 0
    else:
        number_of_pids -= 2
    result["number_of_pids_running"] = number_of_pids
    result = json.dumps(result)
    return result
