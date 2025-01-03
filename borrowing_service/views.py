from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter

from borrowing_service.filters import BorrowingFilter
from borrowing_service.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from borrowing_service.models import Borrowing


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Borrowing.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BorrowingFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(name="user_id", type=int, location="path"),
            OpenApiParameter(name="is_active", type=bool, location="path"),
        ],
        description="Return a borrowed book to the library inventory",
        responses={
            200: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            }
        },
        tags=["borrowings"],
        operation_id="return_borrowed_book",
    )
    @action(methods=["POST"], detail=True, url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()
        return Response(
            {"detail": f"{borrowing.book.title} successfully returned!"},
            status=status.HTTP_200_OK,
        )

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "return_book":
            return BorrowingReturnSerializer

        return BorrowingCreateSerializer
