from flask import jsonify, Blueprint, request, make_response
from flask_api import status
from airflow.models import DagRun, XCom
from airflow.exceptions import AirflowException
import logging
import ast 
from airflow.utils import timezone
from diagnostic_tool.utils import check_and_get_task, check_and_get_taskrun

log = logging.getLogger(__name__)
tasks_blueprint = Blueprint('tasks_api', __name__, url_prefix='/diagnostictool')

@tasks_blueprint.route('/tasks/<string:task_id>', methods=['GET'])
def tasks(task_id):
    try:
        state = request.args.get('state')
        dagruns = get_task_runs(task_id, state)
    except AirflowException as err:
        log.error(err)
        return make_response({'msg': str(err)}, status.HTTP_400_BAD_REQUEST)

    return make_response(jsonify(dagruns), status.HTTP_200_OK)

def get_task_runs(task_id, state=None):
    check_and_get_task(task_id=task_id)

    task_runs = []
    state = state.lower() if state else None
    for run in DagRun.find(dag_id=task_id, state=state):
        res = XCom.get_many(execution_date=run.execution_date, dag_ids=task_id, include_prior_dates=False)
        result = {}
        for r in res:
            re = {}
            try:
                re = ast.literal_eval(r.value) #convert res to dict
            except Exception:
                log.error("Output not found corresponding to check " + r.task_id + " OR Output can't be parsed into JSON")
            result[r.task_id] = re  
        task_runs.append({
            'id': run.id,
            'run_id': run.run_id,
            'state': run.state,
            'task_id': run.dag_id,
            'execution_date': run.execution_date.isoformat(),
            'start_date': ((run.start_date or '') and
                           run.start_date.isoformat()),
            'output' : result
        })
    return task_runs

@tasks_blueprint.route('/tasks/<string:task_id>/<string:execution_date>', methods=['GET'])
def task(task_id, execution_date):
    """
    Returns a JSON with a dag_run's public instance variables.
    The format for the exec_date is expected to be
    "YYYY-mm-DDTHH:MM:SS", for example: "2016-11-16T11:34:15". This will
    of course need to have been encoded for URL in the request.
    """
    # Convert string datetime into actual datetime
    try:
        execution_date = timezone.parse(execution_date)
    except ValueError:
        error_message = (
            'Given execution date, {}, could not be identified '
            'as a date. Example date format: 2015-11-16T14:34:15+00:00'.format(
                execution_date))
        log.error(error_message)
        return make_response({'msg': error_message}, status.HTTP_400_BAD_REQUEST)
    try:
        task_run = get_task_run(task_id, execution_date)
    except AirflowException as err:
        log.error(err)
        return make_response({'msg': str(err)}, err.status_code)
    return make_response(jsonify(task_run), status.HTTP_200_OK)

def get_task_run(task_id, execution_date):
    """Return the task object identified by the given dag_id and task_id.
    :param dag_id: DAG id
    :param execution_date: execution date
    :return: Dictionary storing state of the object
    """

    task = check_and_get_task(task_id=task_id)

    taskrun = check_and_get_taskrun(task, execution_date)
    result = XCom.get_many(execution_date=execution_date, dag_ids=task_id, include_prior_dates=False)
    output = {}
    for r in result:
        res = {}
        try:
            res = ast.literal_eval(r.value) #convert res to dict
        except Exception:
            log.error("Output not found corresponding to check " + r.task_id + " OR Output can't be parsed into JSON")
        output[r.task_id] = res
    return {
        'state': taskrun.get_state(),
        'id' : taskrun.id,
        'run_id' : taskrun.run_id,
        'execution_date': taskrun.execution_date.isoformat(),
        'start_date': ((taskrun.start_date or '') and
                           taskrun.start_date.isoformat()),
        'task_id': taskrun.dag_id,
        'output': output
    }
