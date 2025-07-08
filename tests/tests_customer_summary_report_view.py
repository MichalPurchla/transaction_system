from decimal import Decimal
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.models import Customer, Product, Transaction


@pytest.mark.django_db
class TestCustomerSummaryView:

    def setup_method(self):
        self.customer = Customer.objects.create(
            id=uuid4(),
            name="John Doe",
            email="john@example.com",
            phone_number="123456789",
            address="Test Address",
            is_active=True,
        )

        self.product = Product.objects.create(id=uuid4(), name="Test Product", description="Desc")

        self.transactions = [
            Transaction.objects.create(
                transaction_id=uuid4(),
                timestamp=timezone.now(),
                amount=Decimal("100.00"),
                currency="USD",
                customer=self.customer,
                product=self.product,
                quantity=2,
            )
            for _ in range(3)
        ]

    def test_customer_summary_success(self, auth_client):
        url = reverse("customer_summary", args=[self.customer.id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == str(self.customer.id)
        assert data["total_spent_pln"] == 1200.0
        assert data["unique_products"] == 1
        assert data["last_transaction_date"] is not None

    def test_customer_summary_no_transactions(self, auth_client):
        self.transactions.clear()
        Transaction.objects.all().delete()

        url = reverse("customer_summary", args=[self.customer.id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == str(self.customer.id)
        assert data["total_spent_pln"] == 0
        assert data["unique_products"] == 0
        assert data["last_transaction_date"] is None

    def test_customer_summary_not_found(self, auth_client):
        url = reverse("customer_summary", args=[uuid4()])
        response = auth_client.get(url)
        assert response.status_code == 404
