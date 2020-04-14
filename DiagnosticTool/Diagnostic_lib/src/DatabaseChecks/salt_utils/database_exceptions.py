class DiagnosticToolException(Exception):
    "this is a base class for all exceptions related to Diagnostic Tool"

class DBParameterNotFoundException(DiagnosticToolException):
    "This exception is thrown when db parameters not found"
