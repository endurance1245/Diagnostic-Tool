activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))
        
class AWSConnectionException(Exception):
    "This is Base exception class for AWS Connection"
    pass

class RDSConnectionException(Exception):
    "This is Base exception class for RDS Connection"
    pass

class RDSClientException(RDSConnectionException):
    "This exception is thrown when rds client can not be formed"
    pass

class ResourceIdNotFoundException(RDSConnectionException):
    "This exception is thrown when resource id not found for a campaign db or incorrect db name passed"
    pass

class PerformanceInsightsConnectionException(Exception):
    "This is Base Exception class for Performance Insights Connection"
    pass

class CloudWatchConnectionException(Exception):
    "This is Base Exception class for Cloud Watch Connection"
    pass
