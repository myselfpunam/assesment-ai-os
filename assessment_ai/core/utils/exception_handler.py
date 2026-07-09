import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'message': _extract_message(response.data),
            'errors': response.data,
            'status_code': response.status_code,
        }
        response.data = error_data
        return response

    # Unhandled exceptions
    logger.exception("Unhandled exception", exc_info=exc)
    return Response(
        {
            'success': False,
            'message': 'An unexpected error occurred. Please try again later.',
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_message(data):
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        # Return first error message found
        for key, val in data.items():
            if isinstance(val, list) and val:
                return f"{key}: {val[0]}"
        return 'Validation failed.'
    if isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred.'
