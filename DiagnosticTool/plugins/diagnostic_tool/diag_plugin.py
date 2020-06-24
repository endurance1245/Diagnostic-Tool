from airflow.plugins_manager import AirflowPlugin

from diagnostic_tool.api.dag_runs import tasks_blueprint
from diagnostic_tool.api.check_runs import checks_blueprint
from diagnostic_tool.api.dag_run_check import dag_run_check_blueprint
from diagnostic_tool.api.dag_pause_state import dag_pause_state_blueprint
from diagnostic_tool.operators.salt_operator import SaltOperator

class DiagnosticToolPlugin(AirflowPlugin):
    name = "diagnostic_tool_plugin"
    
    flask_blueprints = [
        tasks_blueprint, 
        checks_blueprint,
        dag_run_check_blueprint,
        dag_pause_state_blueprint
    ]

    operators = [
        SaltOperator
    ]
