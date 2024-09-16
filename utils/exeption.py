class SimpleException(Exception):
    msg: str

    def __init__(self, msg: str) -> None:
        self.msg: str = msg
        super().__init__(msg)


class ExplicitException(Exception):
    msg: str
    description: str

    def __init__(self, msg: str, description: str = "") -> None:
        self.msg: str = msg
        self.description: str = description
        super().__init__(msg, description)
