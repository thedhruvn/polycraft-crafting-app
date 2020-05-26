## Custom exceptions


class BadExtensionException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class ItemNotFoundException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class BadSubgraphForMermaidException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg
