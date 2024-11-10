# APIEndpointError.py
class APIEndpointError(Exception):
    def __init__(self, message="API endpoint has changed. Script will terminate."):
        self.message = message
        super().__init__(self.message)
