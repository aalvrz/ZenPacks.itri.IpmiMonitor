

class IpmitoolError(Exception):
    """Generic exception for ipmitool"""

    def __init__(self, msg, original_exception):
        super(IpmitoolError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
        