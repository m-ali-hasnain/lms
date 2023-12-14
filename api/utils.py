from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response.status_code == status.HTTP_403_FORBIDDEN:
        response.data = {'sucess': False, 'status_code': status.HTTP_403_FORBIDDEN, 
                         'message': response.data['detail']}

    return response