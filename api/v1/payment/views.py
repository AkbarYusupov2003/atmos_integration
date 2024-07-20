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
    permission_classes = ()
    authentication_classes = ()

    def get_user(self):
        return get_object_or_404(get_user_model(), pk=self.request._auth["user_id"])

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
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default=_("Неизвестная ошибка")
                        )
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        # user = self.get_user()
        url = "https://partner.atmos.uz/partner/bind-card/init"
        card_number = request.data.get("card_number", "8600490744313347")
        expiry = request.data.get("expiry", "2410")
        data = {"card_number": card_number, "expiry": expiry}
        response = atmos_request.post(url, data)
        description = response["result"]["description"]
        #
        print(response)
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
                {"error": _("Неизвестная ошибка")},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class AtmosBindCardConfirmAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

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
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default=_("Неизвестная ошибка")
                        )
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/partner/bind-card/confirm"
        transaction_id = request.data.get("transaction_id", 2677)
        otp = request.data.get("otp", "111111")
        data = {"transaction_id": transaction_id, "otp": otp}
        response = atmos_request.post(url, data)
        description = response["result"]["description"]
        #
        print("response", response)
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
                {"error": _("Неизвестная ошибка")},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class AtmosBindCardDialAPIView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "transaction_id": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=["transaction_id"],
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
            }

        )
    )
    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/partner/bind-card/dial"
        transaction_id = request.data.get("transaction_id")
        data = {"transaction_id": transaction_id}
        atmos_request.post(url, data)
        return JsonResponse({"message": "sms sent"})


class AtmosBindCardListAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

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
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default=_("Неизвестная ошибка")
                        )
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
        print("response", response)
        if description == "Нет ошибок":
            return JsonResponse({"card_list": response["card_list"]})
        else:
            return JsonResponse(
                {"error": _("Неизвестная ошибка")},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )


class AtmosBindCardRemoveAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(
        operation_summary="Remove card",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "card_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "token": openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Card removed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            default=_("Неизвестная ошибка")
                        )
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
        print("response", response)
        return JsonResponse({"message": "card deleted"})


# Pay Scheduler
class AtmosPaySchedulerCreateAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/pay-scheduler/create"
        date_start = datetime.datetime.now()
        date_finish = date_start.replace(year=date_start.year+1)
        user_id = "2410"
        amount = 751240000
        cards = "[1666741]"
        phone = "998974445566"
        data = {
            "payment": {
                "date_start": date_start.strftime("%Y-%m-%d"),
                "date_finish": date_finish.strftime("%Y-%m-%d"),
                "login": "998991234567",
                "pay_day": date_start.day,
                "pay_time": "10:00",
                "repeat_interval": 2,
                "repeat_times":  2,
                "ext_id": user_id,
                "repeat_low_balance": True,
                "amount": amount,
                "cards": cards,
                "store_id": settings.ATMOS_STORE_ID,
                "account": phone,
            }
        }
        response = atmos_request.post(url, data)
        print("response", response)
        return JsonResponse({})


class AtmosPaySchedulerConfirmAPIView(APIView):

    def post(self, request, *args, **kwargs):
        url = "https://partner.atmos.uz/pay-scheduler/confirm"
        sсheduler_id = request.data.get("sсheduler_id")
        otp = request.data.get("otp")
        data = {"sсheduler_id": sсheduler_id, "otp": otp}
        response = atmos_request.post(url, data)
        return JsonResponse({})


class AtmosPaySchedulerChangeAPIView(APIView):

    def post(self, request, *args, **kwargs):
        # TODO "delete": True
        url = "https://partner.atmos.uz/pay-scheduler/change"
        data = {
            "sсheduler_id": 75127,
            "delete": False,
            "payment": {
                "date_start": "2022-12-13",
                "date_finish": "2023-12-13",
                "login": "9989881234567",
                "pay_day": 16,
                "pay_time": "14:14",
                "repeat_interval": 2,
                "repeat_times": 10,
                "ext_id": "2410",
                "repeat_low_balance": True,
                "amount": 111110000,
                "cards": "[1666741]",
                "store_id": 7777,
                "account": "998974445566"
            }
        }
        response = atmos_request.post(url, data)
        return JsonResponse({})
