from django.contrib import admin

from payment import models


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "status", "amount", "currency", "payment_service", "created_at", "updated_at")
    list_filter = ("currency", "status", "payment_service", "created_at", "updated_at")
    search_fields = ("amount", )
