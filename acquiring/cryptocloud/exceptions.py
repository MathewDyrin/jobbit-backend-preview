class GeneralError(Exception):
    def __init__(self, *args):
        if args:
            self.msg = args[0]
        else:
            self.msg = None

    def __str__(self, *args, **kwargs):
        if self.msg:
            return f'{self.__class__.__name__}: {self.msg}'


class CryptoCloudCommonExceptions(GeneralError):
    error_codes = {
        401: "Unauthenticated: Bad API KEY provided"
    }

    def __init__(self, error: int):
        code_error = error
        if code_error in self.error_codes:
            msg_error = self.error_codes[code_error]
            super().__init__(msg_error)
        else:
            msg_error = None
            super().__init__(msg_error)
