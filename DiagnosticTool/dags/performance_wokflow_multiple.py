from datetime import datetime, timedelta
import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators import SaltOperator
from constants import (DEFAULT_EXECUTION_TIMEOUT, DEFAULT_RETRIES, 
                                    DEFAULT_RETRY_DELAY, DEFAULT_START_DATE)

#arguments
args = {
    'owner': 'DiagAirflow',
    'start_date': DEFAULT_START_DATE,
    'concurrency': 1,
    'retries': 0
}

#dags
performance_workflow_multiple_dag = DAG(
    dag_id = 'performance_workflow_multiple',
    description = 'Performance issue due to multiple workflows. To trigger the dag, use the trigger_dag REST API only.',
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
    dag = performance_workflow_multiple_dag,
)

opr_check_swap_usage = SaltOperator(
    task_id='check_swap_usage',
    module_name='health_check.get_swap_memory_usage',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_multiple_dag,
)

opr_check_mta = SaltOperator(
    task_id='check_mta',
    module_name='health_check.get_mta_usage',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_multiple_dag,
)

opr_check_cpu = SaltOperator(
    task_id='check_cpu',
    module_name='health_check.get_load_average',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_multiple_dag,
)

opr_count_pid = SaltOperator(
    task_id='count_of_pid',
    module_name='health_check.get_number_of_pids',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_multiple_dag,
)

#check how many workflows are running on the system
opr_count_workflow = SaltOperator(
    task_id='count_workflow_and_state',
    module_name='workflow_count_and_state_wrapper.workflow_count_and_state_caller',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_multiple_dag,
)

#Check dailyworkflow status 
opr_workflow_daily_service = SaltOperator(
    task_id='check_workflow_daily_service',
    module_name='workflow_daily_service_wrapper.workflow_daily_service_caller', #to invoke the function of workflow status
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_multiple_dag,
)

#dependencies
opr_check_memory_usage
opr_check_swap_usage
opr_check_mta
opr_check_cpu
opr_count_pid
opr_count_workflow
opr_workflow_daily_service
