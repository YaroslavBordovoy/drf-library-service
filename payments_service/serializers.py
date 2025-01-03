from rest_framework import serializers

from payments_service.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("session_url", "session_id")
