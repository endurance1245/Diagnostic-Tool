from flask import jsonify, request, Response
from airflow.models import DagBag, DagModel, DagRun
from airflow.utils.db import provide_session
from diagnostic_tool.exceptions import CheckNotFoundException, TaskNotFoundException, TaskRunNotFoundException

def check_and_get_task(task_id, check_id=None):
    """Checks that task exists and in case it is specified that check exist"""
    dag_model = DagModel.get_current(task_id)
    if dag_model is None:
        raise TaskNotFoundException("Task id {} not found in DagModel".format(task_id))

    dagbag = DagBag(
        dag_folder=dag_model.fileloc,
    )
    try:
        task = dagbag.get_dag(task_id)
    except TaskNotFoundException as err:
        raise TaskNotFoundException(err) 

    if check_id and not task.has_task(check_id):
        error_message = 'Check {} not found in task {}'.format(check_id, task_id)
        raise CheckNotFoundException(error_message)
    return task

def check_and_get_taskrun(task, run_id):
    """Get DagRun object and check that it exists"""
    taskrun = get_taskrun(task=task, run_id=run_id)
    if not taskrun:
        error_message = ('Dag Run for run_id {} not found in dag {}'
                         .format(run_id, task.dag_id))
        raise TaskRunNotFoundException(error_message)
    return taskrun

@provide_session
def get_taskrun(task, run_id, session=None):
    """Returns the dag run for a given run_id if it exists, otherwise none."""
    dagrun = (
        session.query(DagRun)
        .filter(
            DagRun.dag_id == task.dag_id,
            DagRun.run_id == run_id)
        .first())

    return dagrun
