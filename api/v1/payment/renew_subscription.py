from django.conf import settings
from django.contrib.auth import get_user_model

from api.v1.payment.services import atmos_request
from api.v1.payment.services.transaction import TransactionManager
from payment import models


def renew():
    # if user turned on auto-pay and does not have enough money on balance
    user = get_user_model().objects.get(pk=1)
    card_tokens = models.CardToken.objects.filter(owner=user, is_active=True)
    for card_token in card_tokens:
        # create transaction
        url = "https://partner.atmos.uz/merchant/pay/create"
        amount = 1 * 100
        order_id = 1
        lang = "ru"
        data = {
            "amount": amount, "account": order_id,
            "store_id": str(settings.ATMOS_STORE_ID), "lang": lang
        }
        response = atmos_request.post(url, data)
        if response["result"]["code"] == "OK":
            # pre apply
            transaction_id = response["transaction_id"]
            transaction = TransactionManager.create_instance(data={
                "order_id": order_id,
                "transaction_id": transaction_id,
                "payment_service": models.Transaction.PaymentServiceChoices.atmos,
                "amount": amount,
            })
            url = "https://partner.atmos.uz/merchant/pay/pre-apply"
            data = {
                "card_token": card_token.token,
                "store_id": settings.ATMOS_STORE_ID,
                "transaction_id": transaction_id,
            }
            response = atmos_request.post(url, data)
            if response["result"]["code"] == "OK":
                # apply
                url = "https://partner.atmos.uz/merchant/pay/apply-ofd"
                otp = 111111
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
                    # TODO extend subscription
