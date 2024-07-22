import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from api.v1.payment.services import atmos_request
from api.v1.payment import serializers
from api.v1.payment.services.transaction import TransactionManager
from payment import models


# Merchant
class AtmosMerchantCreateAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(
        operation_summary="Create transaction",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "amount": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=["amount"],
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Transaction created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "transaction_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                description="Unexpected error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING,)
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/merchant/pay/create"
        amount = request.data.get("amount")
        # TODO create order for user
        order_id = "1"
        data = {
            "amount": amount, "account": order_id, # "terminal_id": "TODO",
            "store_id": str(settings.ATMOS_STORE_ID), "lang": "ru"
        }
        response = atmos_request.post(url, data)
        if response["result"]["code"] == "OK":
            TransactionManager.create_instance(data={
                "transaction_id": response["transaction_id"],
                "payment_service": models.Transaction.PaymentServiceChoices.atmos,
                "amount": amount,
            })
            return JsonResponse(
                {"transaction_id": response["transaction_id"]},
                status=status.HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class AtmosMerchantPreApplyAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(
        operation_summary="Pre apply transaction",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "card_token": openapi.Schema(type=openapi.TYPE_STRING),
                "transaction_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=["card_token", "transaction_id"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Transaction pre applied",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, default=_("Transaction pre applied")),
                    }
                )
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                description="Unexpected error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING,)
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/merchant/pay/pre-apply"
        card_token = request.data.get("card_token")
        transaction_id = request.data.get("transaction_id")
        # TODO check owner of transaction
        data = {
            "card_token": card_token,
            "store_id": settings.ATMOS_STORE_ID,
            "transaction_id": transaction_id,
        }
        response = atmos_request.post(url, data)
        if response["result"]["code"] == "OK":
            return JsonResponse(
                {"message": _("Transaction pre applied")},
                status=status.HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class AtmosMerchantApplyAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(
        operation_summary="Apply transaction",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "transaction_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=["transaction_id", ],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Transaction applied",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, default=_("Transaction applied")),
                    }
                )
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                description="Unexpected error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/merchant/pay/apply-ofd"
        transaction_id = request.data.get("transaction_id")
        try:
            transaction = models.Transaction.objects.get(transaction_id=transaction_id)
        except models.Transaction.DoesNotExist:
            return JsonResponse(
                {"error": _("Неизвестная ошибка")},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        # TODO check owner of transaction
        otp = request.data.get("otp", 111111)
        data = {
            "transaction_id": transaction_id,
            "otp": otp,
            "store_id": settings.ATMOS_STORE_ID,
        }
        response = atmos_request.post(url, data)
        if response["result"]["code"] == "OK":
            TransactionManager.update_instance(
                transaction,
                data={"status": models.Transaction.StatusChoices.paid}
            )
            return JsonResponse(
                {"message": _("Transaction applied")},
                status=status.HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class AtmosMerchantGetAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(
        operation_summary="Get transaction",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "transaction_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=["transaction_id"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Transaction retrieved",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success_trans_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "account": openapi.Schema(type=openapi.TYPE_STRING),
                        "amount": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "confirmed": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "prepay_time": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "confirm_time": openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                description="Unexpected error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING,)
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/merchant/pay/get"
        transaction_id = request.data.get("transaction_id")
        try:
            transaction = models.Transaction.objects.get(transaction_id=transaction_id)
        except models.Transaction.DoesNotExist:
            return JsonResponse(
                {"error": _("Неизвестная ошибка")},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        # TODO check owner of transaction
        data = {
            "store_id": settings.ATMOS_STORE_ID,
            "transaction_id": transaction_id,
        }
        response = atmos_request.post(url, data)
        store_transaction = response.get("store_transaction")
        if store_transaction:
            return JsonResponse(
                {
                    "success_trans_id": store_transaction.get("success_trans_id"),
                    "account": store_transaction.get("account"),
                    "amount": store_transaction.get("amount"),
                    "confirmed": store_transaction.get("confirmed"),
                    "prepay_time": store_transaction.get("prepay_time"),
                    "confirm_time": store_transaction.get("confirm_time"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
