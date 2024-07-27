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
from payment import models


# Bind Card
class AtmosBindCardInitAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="Initializes card binding",
        request_body=serializers.AtmosBindCardInitSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Already available",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "card_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "pan": openapi.Schema(type=openapi.TYPE_STRING),
                        "expiry": openapi.Schema(type=openapi.TYPE_STRING),
                        "card_holder": openapi.Schema(type=openapi.TYPE_STRING),
                        "balance": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "phone": openapi.Schema(type=openapi.TYPE_STRING),
                        "card_token": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            status.HTTP_201_CREATED: openapi.Response(
                description="Sends OTP to card owner",
                schema=serializers.AtmosBindCardInitSerializer
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default=_("Неправильные параметры")
                        )
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
        url = "https://partner.atmos.uz/partner/bind-card/init"
        card_number = request.data.get("card_number", "8600490744313347")
        expiry = request.data.get("expiry", "2410")
        data = {"card_number": card_number, "expiry": expiry}
        response = atmos_request.post(url, data)
        description = response["result"]["description"]
        #
        if description == "Нет ошибок":
            return JsonResponse(
                {
                    "transaction_id": response["transaction_id"],
                    "phone": response["phone"],
                },
                status=status.HTTP_201_CREATED,
            )
        elif description == "У партнера имеется указанная карта":
            return JsonResponse(
                response["data"], status=status.HTTP_200_OK,
            )
        elif description == "Неправильные параметры":
            return JsonResponse(
                {"error": _("Неправильные параметры")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class AtmosBindCardConfirmAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="Confirm card binding",
        request_body=serializers.AtmosBindCardConfirmSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Card confirmed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default=_("Карта подтверждена")
                        ),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default=_("Неправильные параметры")
                        )
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
        url = "https://partner.atmos.uz/partner/bind-card/confirm"
        transaction_id = request.data.get("transaction_id") # 2677
        otp = request.data.get("otp") # "111111"
        data = {"transaction_id": transaction_id, "otp": otp}
        response = atmos_request.post(url, data)
        description = response["result"]["description"]
        #
        if description == "Нет ошибок":
            return JsonResponse(
                {"message": _("Карта подтверждена")}, status=status.HTTP_200_OK
            )
        elif description == "Неправильный id транзакции":
            return JsonResponse(
                {"error": _("Неправильный id транзакции")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class AtmosBindCardDialAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="Request a call",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "transaction_id": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=["transaction_id"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Card confirmed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, default="sms_sent",
                        ),
                    }
                )
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                description="Unexpected error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, )
                    }
                )
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/partner/bind-card/dial"
        transaction_id = request.data.get("transaction_id")
        data = {"transaction_id": transaction_id}
        response = atmos_request.post(url, data)
        description = response["result"]["description"]
        #
        if description == "Нет ошибок":
            return JsonResponse({"message": "sms sent"})
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )


class AtmosBindCardListAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="Card list",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "page": openapi.Schema(type=openapi.TYPE_INTEGER),
                "page_size": openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Card confirmed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "card_list": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "card_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "card_token": openapi.Schema(type=openapi.TYPE_STRING),
                                    "pan": openapi.Schema(type=openapi.TYPE_STRING),
                                    "expiry": openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        ),
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
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/partner/list-cards"
        page = request.data.get("page")
        page_size = request.data.get("page_size")
        data = dict()
        if page and page_size:
            data["page"] = page
            data["page_size"] = page_size
        response = atmos_request.post(url, data)
        description = response["result"]["description"]
        #
        if description == "Нет ошибок":
            return JsonResponse({"card_list": response["card_list"]})
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )


class AtmosBindCardRemoveAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="Remove card",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "card_id": openapi.Schema(type=openapi.TYPE_INTEGER,),
                "token": openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Card removed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default="card successfully removed",
                        )
                    }
                )
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                description="Unexpected error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, )
                    }
                )
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/partner/remove-card"
        card_id = request.data.get("card_id")
        token = request.data.get("token")
        data = {"id": card_id, "token": token}
        response = atmos_request.post(url, data=data)
        description = response["result"]["description"]
        #
        if description == "Нет ошибок":
            return JsonResponse({"message": "card successfully removed"})
        else:
            return JsonResponse(
                {"error": response["result"]["description"]},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
