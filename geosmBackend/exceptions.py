class appException(Exception):
    msg:str
    def __init__(self, msg:str) -> None:
        self.msg:str= msg
        super().__init__(msg)