from django.apps import AppConfig


class PaymentsServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments_service"

    def ready(self):
        import payments_service.signals
