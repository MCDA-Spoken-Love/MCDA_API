from rest_framework import exceptions


class MyException(exceptions.APIException):
    status_code = 400
    default_detail = 'An error occurred'
    default_code = 'error'
