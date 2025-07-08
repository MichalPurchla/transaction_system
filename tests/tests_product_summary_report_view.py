from decimal import Decimal
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.models import Customer, Product, Transaction


@pytest.mark.django_db
class TestProductSummaryView:

    def setup_method(self):
        self.customer = Customer.objects.create(
            id=uuid4(),
            name="Jane Doe",
            email="jane@example.com",
            phone_number="987654321",
            address="Test Address",
            is_active=True,
        )

        self.product = Product.objects.create(id=uuid4(), name="Test Product", description="Desc")

        self.transactions = [
            Transaction.objects.create(
                transaction_id=uuid4(),
                timestamp=timezone.now(),
                amount=Decimal("50.00"),
                currency="EUR",  # przeliczone na PLN wg kursu 4.3 => 215.0
                customer=self.customer,
                product=self.product,
                quantity=5,
            )
            for _ in range(2)
        ]

    def test_product_summary_success(self, auth_client):
        url = reverse("product_summary", args=[self.product.id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == str(self.product.id)
        # quantity: 2 transakcje x 5 = 10
        assert data["total_quantity_sold"] == 10
        # revenue: 2 transakcje x 50 x 4.3 = 430
        assert data["total_revenue_pln"] == 430.0
        assert data["unique_customers"] == 1

    def test_product_summary_no_transactions(self, auth_client):
        self.transactions.clear()
        Transaction.objects.all().delete()

        url = reverse("product_summary", args=[self.product.id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == str(self.product.id)
        assert data["total_quantity_sold"] == 0
        assert data["total_revenue_pln"] == 0
        assert data["unique_customers"] == 0

    def test_product_summary_not_found(self, auth_client):
        url = reverse("product_summary", args=[uuid4()])
        response = auth_client.get(url)
        assert response.status_code == 404
