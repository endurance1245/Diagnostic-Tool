from flask import jsonify, Blueprint, request, make_response
from airflow.models import DagRun
from airflow.utils.db import provide_session
from airflow.exceptions import AirflowException
import logging
import json
from datetime import datetime, timedelta
from airflow.utils import timezone
from airflow.utils.state import State
from flask_api import status
from diagnostic_tool.utils import check_and_get_task
from diagnostic_tool.exceptions import TaskNotFoundException

START_DELAY= timedelta(minutes = 5)

log = logging.getLogger(__name__)
dag_run_check_blueprint = Blueprint('dag_run_check_api', __name__, url_prefix='/diagnostictool')

@dag_run_check_blueprint.route('/tasks/<string:task_id>/check_dag_run/<string:execution_date>', methods=['GET'])
@provide_session
def check_dag_run(task_id, execution_date, session=None):
    """Returns a JSON with a task's public instance variables. """
    dag_result = {}
    try:
        execution_date = timezone.parse(execution_date)
        start_execution_date = execution_date - START_DELAY
    except ValueError:
        error_message = (
            'Given execution date, {}, could not be identified '
            'as a date. Example date format: 2015-11-16T14:34:15+00:00'.format(
                execution_date))
        log.error(error_message)
        return make_response({'msg': error_message}, status.HTTP_400_BAD_REQUEST)
    if 'instance_name' in request.args:
        instance_name = request.args.get('instance_name')
    else:
        error_message = "provide campaign instance as query parameter"
        log.error(error_message)
        return make_response({'msg': error_message}, status.HTTP_400_BAD_REQUEST)
    try:
        task = check_and_get_task(task_id=task_id)
        qry = session.query(DagRun).filter(
            DagRun.dag_id == task_id,
            DagRun.state == State.RUNNING,
            DagRun.external_trigger == True,
            DagRun.run_id.like("{0}&{1}%".format(instance_name,task_id)),
            DagRun.execution_date.between(start_execution_date,execution_date),
        )
        dag = qry.first()
        if dag is None:
            result = {}
            result["is_running"] = False
            result["msg"] = "No Dag with running state exist within last 5 minutes"
            return make_response(jsonify(result), status.HTTP_200_OK)
        dag_result["run_id"] = dag.run_id
        dag_result["execution_date"] = dag.execution_date.isoformat()
        dag_result["state"] = dag.state
        dag_result["is_running"] = True
        return make_response(jsonify(dag_result), status.HTTP_200_OK)
    except Exception as err:
        log.error(err)
        return make_response({'msg': err}, status.HTTP_400_BAD_REQUEST)
