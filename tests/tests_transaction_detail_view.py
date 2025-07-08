from decimal import Decimal
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.models import Customer, Product, Transaction


@pytest.mark.django_db
class TestTransactionDetailView:

    def setup_method(self):
        self.customer = Customer.objects.create(
            id=uuid4(),
            name="John Doe",
            email="john@example.com",
            phone_number="123456789",
            address="Test Address",
            is_active=True,
        )
        self.product = Product.objects.create(id=uuid4(), name="Test Product", description="Super product")
        self.transaction = Transaction.objects.create(
            transaction_id=uuid4(),
            timestamp=timezone.now(),
            amount=Decimal("19.99"),
            currency="USD",
            customer=self.customer,
            product=self.product,
            quantity=1,
        )

    def test_transaction_detail_success(self, auth_client):
        url = reverse("transaction_detail", args=[self.transaction.transaction_id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == str(self.transaction.transaction_id)
        assert data["amount"] == "19.99"
        assert data["currency"] == "USD"
        assert data["customer_id"] == str(self.customer.id)
        assert data["product_id"] == str(self.product.id)
        assert data["quantity"] == 1

    def test_transaction_detail_not_found(self, auth_client):
        from uuid import uuid4

        url = reverse("transaction_detail", args=[uuid4()])

        response = auth_client.get(url)

        assert response.status_code == 404

    def test_no_auth_token(self, client):
        url = reverse("transaction_detail", args=[self.transaction.transaction_id])
        response = client.get(url)
        assert response.status_code == 403
