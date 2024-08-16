from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 8

class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_page_number(self, request, paginator):
        return int(request.GET.get('pageNumber', DEFAULT_PAGE))

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total': self.page.paginator.count,
            'page_number': int(self.request.GET.get('pageNumber', DEFAULT_PAGE)),
            'page_size': int(self.request.GET.get('pageSize', self.page_size)),
            'statusCode': status.HTTP_200_OK,
            'status': 'OK',
            'message': 'Success',
            'data': data
        })