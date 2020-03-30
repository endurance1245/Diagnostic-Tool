from airflow.plugins_manager import AirflowPlugin

from diagnostic_tool.api.dag_runs import tasks_blueprint
from diagnostic_tool.api.check_runs import checks_blueprint

class DiagnosticToolPlugin(AirflowPlugin):
    name = "diagnostic_tool_plugin"
    
    flask_blueprints = [
        tasks_blueprint, 
        checks_blueprint
    ]
