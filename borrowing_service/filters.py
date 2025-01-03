from django_filters import rest_framework

from borrowing_service.models import Borrowing


class BorrowingFilter(rest_framework.FilterSet):
    is_active = rest_framework.BooleanFilter(method="filter_is_active", label="Returned")
    user_id = rest_framework.NumberFilter(field_name="user__id")

    class Meta:
        model = Borrowing
        fields = ("is_active", "user_id")

    def filter_is_active(self, queryset, name, value):
        if value:
            return queryset.filter(
                borrow_date__isnull=False, actual_return_date__isnull=True
            ).distinct()
        return queryset.extend(
            borrow_date__isnull=False, actual_return_date__isnull=True
        ).distinct()
