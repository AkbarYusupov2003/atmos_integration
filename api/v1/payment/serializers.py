from rest_framework import serializers


class AtmosBindCardInitSerializer(serializers.Serializer):
    card_number = serializers.CharField()
    expiry = serializers.CharField()


class AtmosBindCardConfirmSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    otp = serializers.CharField()
