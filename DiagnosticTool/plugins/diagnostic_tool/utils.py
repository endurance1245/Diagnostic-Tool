from flask import jsonify, request, Response
from airflow.models import DagBag, DagModel, DagRun
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

def check_and_get_taskrun(task, execution_date):
    """Get DagRun object and check that it exists"""
    taskrun = task.get_dagrun(execution_date=execution_date)
    if not taskrun:
        error_message = ('Dag Run for date {} not found in dag {}'
                         .format(execution_date, task.dag_id))
        raise TaskRunNotFoundException(error_message)
    return taskrun
