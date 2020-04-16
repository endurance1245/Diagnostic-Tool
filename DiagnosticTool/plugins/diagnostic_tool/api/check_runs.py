from flask import jsonify, Blueprint, request, make_response
from airflow.models import DagRun, XCom
from airflow.exceptions import AirflowException
import logging
import json
from airflow.utils import timezone
from flask_api import status
from diagnostic_tool.exceptions import CheckInstanceNotFoundException
from diagnostic_tool.utils import check_and_get_task, check_and_get_taskrun

log = logging.getLogger(__name__)
checks_blueprint = Blueprint('checks_api', __name__, url_prefix='/diagnostictool')

@checks_blueprint.route('/tasks/<string:task_id>/checks/<string:check_id>', methods=['GET'])
def checks(task_id, check_id):
    """Returns a JSON with a task's public instance variables. """
    try:
        check_info = get_check(task_id, check_id)
    except AirflowException as err:
        log.error(err)
        return make_response({'msg': str(err)}, err.status_code)

    # JSONify and return.
    json_result = {k: str(v)
              for k, v in vars(check_info).items()
              if not k.startswith('_')}
    return make_response(jsonify(json_result), status.HTTP_200_OK)

@checks_blueprint.route('/tasks/<string:task_id>/<string:execution_date>/checks/<string:check_id>', methods=['GET'])
def check(task_id, execution_date, check_id):
    """
    Returns a JSON with a check instance's public instance variables with output.
    The format for the execution_date is expected to be
    "YYYY-mm-DDTHH:MM:SS.microseconds", for example: "2016-11-16T11:34:15.123212".
    """

    # Convert string datetime into actual datetime
    try:
        execution_date = timezone.parse(execution_date)
    except ValueError:
        error_message = (
            'Given execution date, {}, could not be identified '
            'as a date. Example date format: 2015-11-16T14:34:15+00:00'
            .format(execution_date))
        log.error(error_message)
        return make_response({'msg': error_message}, status.HTTP_400_BAD_REQUEST)

    try:
        check_instance = get_check_instance(task_id, check_id, execution_date)
        check_result = XCom.get_one(dag_id=task_id, task_id=check_id, execution_date=execution_date)
    except AirflowException as err:
        log.error(err)
        return make_response({'msg': str(err)}, err.status_code)

    # JSONify and return.
    json_result = {
              k: str(v)
              for k, v in vars(check_instance).items()
              if not k.startswith('_')
            }
    check_result_json = {}
    try:
        check_result_json = json.loads(check_result) #convert res to dict
    except Exception:
        if "not" in r.value:
            err = "Output not available for " + check_id
        else:
            err = "Output can't be parsed into JSON for " + check_id
        log.error(err)
        check_result_json['error'] = err         
    json_result['output'] = check_result_json
    return make_response(jsonify(json_result), status.HTTP_200_OK)

def get_check(task_id, check_id):
    """Return the task object identified by the given task_id and check_id."""
    task = check_and_get_task(task_id, check_id)

    # Return the checks.
    return task.get_task(check_id)

def get_check_instance(task_id, check_id, execution_date):
    task = check_and_get_task(task_id, check_id)

    taskrun = check_and_get_taskrun(task=task, execution_date=execution_date)
    
    # Get check instance object and check that it exists
    check_instance = taskrun.get_task_instance(check_id)

    if not check_instance:
        error_message = ('Check {} instance for date {} not found'
                         .format(check_id, execution_date))
        raise CheckInstanceNotFoundException(error_message)

    return check_instance
