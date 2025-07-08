from decimal import Decimal
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.models import Transaction


@pytest.mark.django_db
class TestProductSummaryView:

    def setup_method(self):
        self.customer_id = uuid4()

        self.product_id = uuid4()

        self.transactions = [
            Transaction.objects.create(
                transaction_id=uuid4(),
                timestamp=timezone.now(),
                amount=Decimal("50.00"),
                currency="EUR",
                customer_id=self.customer_id,
                product_id=self.product_id,
                quantity=5,
            )
            for _ in range(2)
        ]

    def test_product_summary_success(self, auth_client):
        url = reverse("product_summary", args=[self.product_id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == str(self.product_id)
        assert data["total_quantity_sold"] == 10
        assert data["total_revenue_pln"] == 430.0
        assert data["unique_customers"] == 1

    def test_product_summary_no_transactions(self, auth_client):
        self.transactions.clear()
        Transaction.objects.all().delete()

        url = reverse("product_summary", args=[self.product_id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == str(self.product_id)
        assert data["total_quantity_sold"] == 0
        assert data["total_revenue_pln"] == 0
        assert data["unique_customers"] == 0

    def test_product_summary_not_found(self, auth_client):
        url = reverse("product_summary", args=[uuid4()])
        response = auth_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["total_quantity_sold"] == 0
