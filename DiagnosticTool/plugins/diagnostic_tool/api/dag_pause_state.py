from flask import jsonify, Blueprint, request, make_response
from flask_api import status
from airflow.models import DagModel
from airflow.exceptions import AirflowException
import logging
from airflow.www.app import csrf
from airflow.utils.db import provide_session

log = logging.getLogger(__name__)
dag_pause_state_blueprint = Blueprint('check_dag_pause_state_api', __name__, url_prefix='/diagnostictool')

@dag_pause_state_blueprint.route('/tasks/<string:task_id>/paused', methods=['GET'])
@provide_session
def tasks(task_id, session=None):
    try:
        qry = session.query(DagModel).filter(DagModel.dag_id == task_id)
        is_paused = qry.value(DagModel.is_paused)
        if is_paused is None:
            error_message = task_id + " is not exist"
            log.error(error_message)
            return make_response({'msg': error_message}, status.HTTP_400_BAD_REQUEST)
        else:
            return make_response(jsonify({"is_paused" : is_paused}), status.HTTP_200_OK)
    except AirflowException as err:
        log.error(err)
        return make_response({'msg': str(err)}, err.status_code)

@csrf.exempt
@dag_pause_state_blueprint.route('/tasks/<string:task_id>/paused/<string:paused>', methods=['PUT'])
@provide_session
def dag_paused(task_id, paused, session=None):
    """(Un)pauses a dag"""
    if paused == 'true':
        is_paused = True
    elif paused == 'false':
        is_paused = False
    else:
        error_message = "Accepts true or false only"
        log.error(error_message)
        return make_response({'msg': error_message}, status.HTTP_400_BAD_REQUEST) 
    try:
        DagModel.get_dagmodel(task_id).set_is_paused(
            is_paused=is_paused,
        )
        return make_response(jsonify({"is_paused" : is_paused}), status.HTTP_200_OK)
    except AirflowException as err:
        log.error(err)
        return make_response({'msg': str(err)}, err.status_code)
