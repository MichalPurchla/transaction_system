import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.dateparse import parse_datetime


class Transaction(models.Model):
    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
    ]

    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
    )

    customer_id = models.UUIDField()

    product_id = models.UUIDField()

    quantity = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["customer_id"]),
            models.Index(fields=["product_id"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"

    def clean(self):
        allowed_currencies = ["USD", "EUR"]
        if self.currency not in allowed_currencies:
            raise ValidationError(
                f"Currency '{self.currency}' is not allowed. Allowed currencies: {allowed_currencies}"
            )

        if isinstance(self.timestamp, str):
            parsed = parse_datetime(self.timestamp)
            if parsed is None:
                raise ValidationError({"timestamp": f"Invalid datetime format: {self.timestamp}"})
            self.timestamp = parsed
