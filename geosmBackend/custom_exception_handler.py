from rest_framework.views import exception_handler
from geosmBackend.exceptions import appException
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code

    if isinstance(exc,appException):
        if response is  None:
            response =  Response({}, status=status.HTTP_400_BAD_REQUEST)

        error_payload = {
                "status_code": 0,
                "message": "",
                "details": [],
        }
        error = error_payload
        status_code = response.status_code
        error["status_code"] = status_code
        error["message"] = exc.msg
        response.data = error_payload
   
    return response