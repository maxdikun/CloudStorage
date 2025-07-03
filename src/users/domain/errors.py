class ValidationError(Exception):
    def __init__(self, object: str, message: str):
        self.object = object
        self.message = message
        super().__init__("invalid data for field is provided")


class MultiValidationErrors(Exception):
    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        super().__init__("Multiple validation error occurred")


class InvalidCredentials(ValueError):
    pass


class InternalError(Exception):
    def __init__(self):
        super().__init__("Internal service error occurred")
