from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    """Standardized API response builder used by all views."""

    @staticmethod
    def success(data=None, message='Success', status_code=status.HTTP_200_OK):
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status_code,
        )

    @staticmethod
    def created(data=None, message='Created successfully'):
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def error(message='Something went wrong', errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                'success': False,
                'message': message,
                'errors': errors,
            },
            status=status_code,
        )

    @staticmethod
    def not_found(message='Resource not found'):
        return Response(
            {
                'success': False,
                'message': message,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    @staticmethod
    def forbidden(message='You do not have permission to perform this action'):
        return Response(
            {
                'success': False,
                'message': message,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    @staticmethod
    def no_content():
        return Response(status=status.HTTP_204_NO_CONTENT)
