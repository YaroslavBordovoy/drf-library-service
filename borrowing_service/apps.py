from django.apps import AppConfig


class BorrowingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowing_service"

    def ready(self):
        import borrowing_service.signals
