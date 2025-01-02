from rest_framework import routers

from borrowing_service.views import BorrowingViewSet

router = routers.DefaultRouter()

router.register("borrowings", BorrowingViewSet)

urlpatterns = router.urls

app_name = "borrowing"
