from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .responses import custom_response
import math

class ThreePerPagePagination(PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)

        pagination_data = {
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        }

        return custom_response(data=pagination_data, message='목록 조회 성공')