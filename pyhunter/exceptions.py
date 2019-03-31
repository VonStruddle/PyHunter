
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
    pass