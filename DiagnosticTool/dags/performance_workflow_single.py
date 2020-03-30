from datetime import datetime, timedelta
import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators import SaltOperator
from dags.dag_constants import (DEFAULT_EXECUTION_TIMEOUT, DEFAULT_RETRIES, 
                                    DEFAULT_RETRY_DELAY, DEFAULT_START_DATE)

#arguments
args = {
    'owner': 'DiagAirflow',
    'start_date': DEFAULT_START_DATE,
    'concurrency': 1,
    'retries': 0
}

#dags
performance_workflow_single_dag = DAG(
    dag_id = 'performance_workflow_single',
    description = 'If there is performance issue due to single workflow. To trigger the dag, use the trigger_dag REST API only.',
    default_args = args,
    schedule_interval = None,
)

#tasks
opr_check_memory_usage = SaltOperator(
    task_id='check_memory_usage',
    module_name='health_check.get_memory_usage',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

opr_check_swap_usage = SaltOperator(
    task_id='check_swap_usage',
    module_name='health_check.get_swap_memory_usage',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

opr_check_mta = SaltOperator(
    task_id='check_mta',
    module_name='health_check.get_mta_usage',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

opr_check_cpu = SaltOperator(
    task_id='check_cpu',
    module_name='health_check.get_load_average',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

opr_count_pid = SaltOperator(
    task_id='count_of_pid',
    module_name='health_check.get_number_of_pids',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

#dependencies
opr_check_memory_usage
opr_check_swap_usage
opr_check_mta
opr_check_cpu
opr_count_pid
