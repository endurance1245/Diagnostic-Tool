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

opr_workflow_type = SaltOperator(
    task_id='count_of_pid',
    module_name='workflow_type_wrapper.workflow_type_caller',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

#Check workflow status if internal is given
opr_workflow_status = SaltOperator(
    task_id='check_workflow_satus',
    module_name='workflow_status_wrapper.workflow_status_caller', #to invoke the function of workflow status
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

opr_count_workflow = SaltOperator(
    task_id='count_of_pid',
    module_name='count_workflow.workflow_count',
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = performance_workflow_single_dag,
)

#Check  dailyworkflow status if internal is given
opr_workflow_daily_service = SaltOperator(
    task_id='check_workflow_daily_service',
    module_name='workflow_daily_service_wrapper.workflow_daily_service_caller', #to invoke the function of workflow status
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
opr_workflow_type
opr_workflow_status
opr_workflow_daily_service
opr_count_workflow
