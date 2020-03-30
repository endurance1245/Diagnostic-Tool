from airflow.exceptions import AirflowNotFoundException

class CheckInstanceNotFoundException(AirflowNotFoundException):
    """Raise when a Check Instance is not available in the system"""

class CheckNotFoundException(AirflowNotFoundException):
    """Raise when a Check is not available in the system"""

class TaskNotFoundException(AirflowNotFoundException):
    """Raise when a Task is not available in the system"""

class TaskRunNotFoundException(AirflowNotFoundException):
    """Raise when a Task is not available in the system"""
