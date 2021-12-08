class GetOutOfLoop(Exception):
    pass

class CodeError(Exception):
    def __init__(self, message):
        self.message = message
