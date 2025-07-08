from decimal import Decimal
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.models import Transaction


@pytest.mark.django_db
class TestTransactionDetailView:

    def setup_method(self):
        self.customer_id = uuid4()
        self.product_id = uuid4()
        self.transaction = Transaction.objects.create(
            transaction_id=uuid4(),
            timestamp=timezone.now(),
            amount=Decimal("19.99"),
            currency="USD",
            customer_id=self.customer_id,
            product_id=self.product_id,
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
        assert data["customer_id"] == str(self.customer_id)
        assert data["product_id"] == str(self.product_id)
        assert data["quantity"] == 1

    def test_transaction_detail_not_found(self, auth_client):
        url = reverse("transaction_detail", args=[uuid4()])

        response = auth_client.get(url)

        assert response.status_code == 404

    def test_no_auth_token(self, client):
        url = reverse("transaction_detail", args=[self.transaction.transaction_id])
        response = client.get(url)
        assert response.status_code == 403
