from django.contrib import admin

from .models import Customer, Product, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "timestamp",
        "amount",
        "currency",
        "customer",
        "product",
        "quantity",
        "created_at",
    )
    search_fields = ("transaction_id", "customer__name", "product__name")
    list_filter = ("currency", "timestamp", "created_at")
    ordering = ("-timestamp",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "created_at")
    search_fields = ("id", "name", "email")
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("id", "name")
    ordering = ("name",)
