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


# Pay Scheduler
class AtmosPaySchedulerCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        # from request - user, amount,
        #
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
                "login": phone,
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
