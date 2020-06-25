from datetime import datetime as dt
import datetime
import flask
from flask_api import status
import json
import ast
import requests
import pendulum
import xml.etree.ElementTree as ET
from flask import Blueprint, request, jsonify, make_response


dag_blueprint = Blueprint('test_api', __name__, url_prefix='/diagnostictool')


@dag_blueprint.route('/checkinstance/<string:instanceurl>', methods =['GET'])
def checkInstance(instanceurl):
    '''
    This api checks the instance url by performing the r/test
    '''
    if instanceurl:
        URL = 'https://'+instanceurl+'/r/test'
        print(URL)
        try:
            result = requests.get(URL, headers = {'Content-type' : 'application/json','Accept': 'text/xml'})
            xmlTag = ET.fromstring(result.content)
            dictionary = xmlTag.attrib
            resultValue = json.dumps(dictionary, indent = 4)
            return make_response(resultValue, result.status_code)
        except Exception as er:
            error_message = er
            return make_response({'Error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        error_message = 'Not valid instance'
        return make_response({'Error': error_message}, status.HTTP_400_BAD_REQUEST)


@dag_blueprint.route('/tasks/<string:taskId>/trigger', methods=['POST'])
def setTrigger(taskId):
    '''
    This api is used to trigger the task.
    '''
    urlParameters = json.loads(request.get_data())
    run_id = urlParameters['run_id']
    time = urlParameters['execution_date']
    conf = urlParameters['conf']
    print(conf)
    if run_id and time:
        execution_date = time
        URL = 'http://10.0.0.183:8080/api/experimental/dags/'+taskId+'/dag_runs'
        try:
            result = requests.post(URL, headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}, data = json.dumps({'run_id' : run_id,'execution_date': execution_date, 'conf': conf}))
            resultValue = result.json()
            return make_response(resultValue, result.status_code)
        except Exception as er:
            error_message = er
            return make_response({'Error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        error_message = 'taskId or executionTimeStamp not mentioned'
        return make_response({'Error': error_message}, status.HTTP_400_BAD_REQUEST)



@dag_blueprint.route('/tasks/<string:taskId>/<string:runId>', methods =['GET'])
def getOutput(taskId, runId):
    '''
    This api get all the output of airflow 
    '''
    if taskId and runId:
        URL = 'http://10.0.0.183:8080/diagnostictool/tasks/'+taskId+'/'+runId
        print(URL)
        try:
            result = requests.get(URL, headers = {'Content-type' : 'application/json','Accept': 'application/json'})
            resultValue = result.json()
            if 'output' in resultValue:
                return make_response(resultValue['output'], result.status_code)
            else:
                return make_response(resultValue, result.status_code)
        except Exception as er:
            error_message = er
            return make_response({'Error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        error_message = 'taskId or RunId not mentioned'
        return make_response({'Error': error_message}, status.HTTP_400_BAD_REQUEST)


@dag_blueprint.route('/tasks/<string:taskId>/check_dag_run/<string:executionTimeStamp>/<string:instanceName>')
def checkRunningDag(taskId, executionTimeStamp,instanceName):
    '''
    This api to check  if  Dag is already running
    '''
    if taskId and executionTimeStamp and instanceName:
        URL = 'http://10.0.0.183:8080/diagnostictool/tasks/'+taskId+'/check_dag_run/'+executionTimeStamp+'?instance_name='+instanceName
        
        try:
            result = requests.get(URL, headers = {'Content-type' : 'application/json','Accept': 'application/json'})
            resultValue = result.json()
            return make_response(resultValue, result.status_code)
        except Exception as er:
            error_message = er
            return make_response({'Error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        error_message = 'taskId or executionTimeStamp or InstanceName not mentioned'
        return make_response({'Error': error_message}, status.HTTP_400_BAD_REQUEST)


@dag_blueprint.route('/tasks/<string:taskId>/paused')
def checkPausedDag(taskId):
    '''
    This api checks if the dag is paused and if paused it unpauses the dag
    '''
    if taskId:
        URL = 'http://10.0.0.183:8080/diagnostictool/tasks/'+taskId+'/paused'
        print(URL)
        try:
            result = requests.get(URL, headers = {'Content-type' : 'application/json','Accept': 'application/json'})
            resultValue = result.json()
            print(resultValue)
            if 'is_paused' in resultValue:
                print(resultValue['is_paused'])
                if (resultValue['is_paused']):
                    url = 'http://10.0.0.183:8080/diagnostictool/tasks/'+taskId+'/paused/false'
                    restart = requests.put(URL, headers = {'Content-type' : 'application/json','Accept': 'application/json'})
                    resultPaused = result.json()
                    return make_response(resultPaused, result.status_code)
                else:
                    return make_response(resultValue, result.status_code)
            else:
                 return make_response(resultValue, result.status_code)
        except Exception as er:
            error_message = er
            return make_response({'Error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        error_message = 'taskId not mentioned'
        return make_response({'Error': error_message}, status.HTTP_400_BAD_REQUEST)


