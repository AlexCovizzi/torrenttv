class FormatError(ValueError):

    def __init__(self, message):
        super().__init__(str(message))


class ValidationError(ValueError):

    def __init__(self, message):
        super().__init__(str(message))


class NotSupportedError(Exception):

    def __init__(self, message):
        super().__init__(str(message))
