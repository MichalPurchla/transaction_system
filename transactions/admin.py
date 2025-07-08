from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "timestamp",
        "amount",
        "currency",
        "customer_id",
        "product_id",
        "quantity",
        "created_at",
    )
    search_fields = ("transaction_id", "customer_id", "product_id")
    list_filter = ("currency", "timestamp", "created_at")
    ordering = ("-timestamp",)
