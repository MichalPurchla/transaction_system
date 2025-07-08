from decimal import Decimal
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.models import Transaction


@pytest.mark.django_db
class TestCustomerSummaryView:

    def setup_method(self):
        self.customer_id = uuid4()
        self.product_id = uuid4()
        self.transactions = [
            Transaction.objects.create(
                transaction_id=uuid4(),
                timestamp=timezone.now(),
                amount=Decimal("100.00"),
                currency="USD",
                customer_id=self.customer_id,
                product_id=self.product_id,
                quantity=2,
            )
            for _ in range(3)
        ]

    def test_customer_summary_success(self, auth_client):
        url = reverse("customer_summary", args=[self.customer_id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == str(self.customer_id)
        assert data["total_spent_pln"] == 1200.0
        assert data["unique_products"] == 1
        assert data["last_transaction_date"] is not None

    def test_customer_summary_no_transactions(self, auth_client):
        self.transactions.clear()
        Transaction.objects.all().delete()

        url = reverse("customer_summary", args=[self.customer_id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == str(self.customer_id)
        assert data["total_spent_pln"] == 0
        assert data["unique_products"] == 0
        assert data["last_transaction_date"] is None

    def test_customer_summary_not_found(self, auth_client):
        url = reverse("customer_summary", args=[uuid4()])
        response = auth_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["unique_products"] == 0
