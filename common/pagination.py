"""Pagination classes and utilities for the portfolio backend.

Usage in a view:
    from common.pagination import LimitOffsetPagination, get_paginated_response

    class ProjectListApi(APIView):
        def get(self, request):
            queryset = Project.objects.filter(is_active=True)
            return get_paginated_response(
                pagination_class=LimitOffsetPagination,
                serializer_class=ProjectOutputSerializer,
                queryset=queryset,
                request=request,
                view=self,
            )
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.response import Response

from common.constants import PaginationDefaults

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework import serializers
    from rest_framework.request import Request
    from rest_framework.views import APIView


class LimitOffsetPagination(_LimitOffsetPagination):
    """Standard portfolio pagination using limit/offset.

    Query params:
        limit:  Number of items to return (default: 10, max: 100).
        offset: Starting position in the full result set (default: 0).

    Response shape (wrapped by get_paginated_response utility):
        {
            "status": "success",
            "data": [...],
            "message": null,
            "meta": {
                "count": 100,
                "limit": 10,
                "offset": 0,
                "next": "http://...?limit=10&offset=10",
                "previous": null
            }
        }
    """

    default_limit = PaginationDefaults.DEFAULT_LIMIT
    max_limit = PaginationDefaults.MAX_LIMIT


def get_paginated_response(
    *,
    pagination_class: type[LimitOffsetPagination],
    serializer_class: type[serializers.Serializer],
    queryset: QuerySet,
    request: Request,
    view: APIView,
) -> Response:
    """Paginate a queryset and return a wrapped success response.

    Decouples pagination from DRF generic views so plain APIViews
    can paginate without inheriting ListModelMixin.

    Args:
        pagination_class: Pagination class to use (LimitOffsetPagination).
        serializer_class: Output serializer class for the queryset items.
        queryset: The QuerySet to paginate and serialize.
        request: Current DRF request (used to build next/previous URLs).
        view: Current API view instance (required by DRF paginator).

    Returns:
        Response with the standard success envelope and meta pagination block.
    """
    from common.responses import success_response  # local import — avoids circular

    paginator = pagination_class()
    paginated_queryset = paginator.paginate_queryset(queryset, request, view=view)
    serializer = serializer_class(
        paginated_queryset, many=True, context={"request": request}
    )

    meta = {
        "count": paginator.count,
        "limit": paginator.get_limit(request),
        "offset": paginator.get_offset(request),
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
    }

    return success_response(data=serializer.data, meta=meta)
