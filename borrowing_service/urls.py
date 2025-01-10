from django.urls import path
from rest_framework import routers

from borrowing_service.views import BorrowingViewSet


router = routers.DefaultRouter()

router.register("", BorrowingViewSet, "borrowing")

urlpatterns = [
    path(
        "borrowings/<int:pk>/return/",
        BorrowingViewSet.as_view({"post": "return_book"}),
        name="borrowing-return",
    ),
]

urlpatterns += router.urls

app_name = "borrowing"
