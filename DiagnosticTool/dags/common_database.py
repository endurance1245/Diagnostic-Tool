import airflow
from airflow import DAG
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

#dag creation 
common_database_checks_dag = DAG(
    dag_id = 'common_database_check',
    description = 'Dag to check issues due to database. Usage - executed by only trigger_dag REST API.',
    default_args = args,
    schedule_interval = None,
)

#tasks
#opeartor to check blocking or deadlock in the database
opr_check_blocking_and_deadlock = SaltOperator(
    task_id='check_blocking_and_deadlock',
    module_name='blocking_and_deadlock_wrapper.blocking_and_deadlock_caller', #to invoke the function of blocking and deadlock
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = common_database_checks_dag,   #associated dag
)

#opeartor to check long running queries in the database
opr_check_long_running_queries = SaltOperator(
    task_id='check_long_running_queries',
    module_name='longqueryfuncwrapper.callablefunc', #to invoke the function of long running query
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = common_database_checks_dag, #associated dag
)

#opeartor to check idle and running queries in the database
opr_check_idle_and_running_state = SaltOperator(
    task_id='check_idle_and_running_state',
    module_name='idle_and_running_state_wrapper.idle_and_running_state_caller', #to invoke the function of idle and running query
    provide_context = True,
    execution_timeout = DEFAULT_EXECUTION_TIMEOUT,
    retries = DEFAULT_RETRIES,
    retry_delay = DEFAULT_RETRY_DELAY,
    dag = common_database_checks_dag, #associated dag
)

#dependencies
#run operators sequentially
opr_check_blocking_and_deadlock >> opr_check_idle_and_running_state >>opr_check_long_running_queries
