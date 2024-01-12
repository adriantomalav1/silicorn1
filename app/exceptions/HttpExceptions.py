from fastapi import HTTPException

class InvalidCredentialsException(HTTPException):
    def __init__(self, status_code=401, detail="Invalid Credentials", headers={"WWW-Authenticate": "Bearer"}):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class ApplicationErrorException(HTTPException):
    def __init__(self, status_code=500, detail="An error internal error occured."):
        super().__init__(status_code=status_code, detail=detail)
