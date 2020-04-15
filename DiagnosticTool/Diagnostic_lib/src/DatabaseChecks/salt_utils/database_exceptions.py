class DiagnosticToolException(Exception):
    "this is a base class for all exceptions related to Diagnostic Tool"

class DBParameterNotFoundException(DiagnosticToolException):
    "This exception is thrown when db parameters not found"

class DataBaseException(DiagnosticToolException):
    "This exception is thrown when there is issue while making db connection or executing a query"

class BadRequestException(DiagnosticToolException):
    "This exception is thrown when wrong parameters is passed to NewRelic"
