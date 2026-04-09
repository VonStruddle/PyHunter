class PyhunterError(Exception):
    """
    Generic exception class for the library
    """
    pass


class MissingCompanyError(PyhunterError):
    pass


class MissingNameError(PyhunterError):
    pass


class HunterApiError(PyhunterError):
    """
    Represents something went wrong in the call to the Hunter API
    """
    def __init__(self, message='Hunter API request failed', status_code=None,
                 error=None, payload=None, endpoint=None, method=None):
        super().__init__(message)
        self.status_code = status_code
        self.error = error
        self.payload = payload
        self.endpoint = endpoint
        self.method = method


class HunterTransportError(PyhunterError):
    """
    Represents transport-level errors while calling Hunter API
    """
    def __init__(self, message='Hunter API transport failed', endpoint=None,
                 method=None):
        super().__init__(message)
        self.endpoint = endpoint
        self.method = method
