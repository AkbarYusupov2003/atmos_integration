from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class CurrencyChoices(models.TextChoices):
    uzs = "UZS", "UZS"
    usd = "USD", "USD"


class Order(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class Transaction(models.Model):
    class StatusChoices(models.TextChoices):
        created = "CREATED", _("Создана")
        canceled = "CANCELED", _("Отменена")
        paid = "PAID", _("Оплачена")

    class PaymentServiceChoices(models.TextChoices):
        payme = "payme", "Payme"
        click = "click", "Click"
        apelsin = "apelsin", "Apelsin"
        paynet = "paynet", "Paynet"
        octo = "octo", "Octo"
        payze = "payze", "Payze"
        uzum = "uzum", "Uzum"
        alif = "alif", "Alif"
        atmos = "atmos", "Atmos"

    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="transactions", verbose_name="Заказ",
    )
    #
    transaction_id = models.CharField(
        "Provider transaction ID", max_length=36, db_index=True, null=True, blank=True
    )
    status = models.CharField(
        "Статус", choices=StatusChoices.choices, default=StatusChoices.created
    )
    payment_service = models.CharField(
        "Платежная служба", max_length=10, choices=PaymentServiceChoices.choices, blank=True, null=True
    )
    currency = models.CharField(
        "Валюта", max_length=12, choices=CurrencyChoices.choices, default=CurrencyChoices.uzs
    )
    amount = models.PositiveIntegerField(verbose_name="Сумма")
    #
    additional_parameters = models.JSONField(
        "Дополнительные параметры", default=dict, blank=True, null=True
    )
    #
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"


class CardToken(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=512)
    phone = models.CharField(max_length=16)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
