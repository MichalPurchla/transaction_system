from decimal import Decimal
from random import choice, randint
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.models import Transaction


@pytest.mark.django_db
class TestTransactionListView:

    def setup_method(self):
        self.products = [uuid4() for i in range(10)]

        self.customers = [uuid4() for i in range(10)]

        self.transactions = [
            Transaction.objects.create(
                transaction_id=uuid4(),
                timestamp=timezone.now(),
                amount=Decimal(str(randint(101, 1001) / 100)),
                currency="USD",
                customer_id=choice(self.customers),
                product_id=choice(self.products),
                quantity=randint(1, 50),
            )
            for _ in range(100)
        ]

    def test_transaction_list_success(self, auth_client):
        url = reverse("transactions_list")
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert len(self.transactions) == data["count"]

    def test_no_auth_token(self, client):
        url = reverse("transactions_list")
        response = client.get(url)
        assert response.status_code == 403

    def test_pagination(self, auth_client):
        page = 2
        url = reverse("transactions_list") + f"?page={page}"
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert page == data["current_page"]
        assert data["has_previous"] is True
        assert data["num_pages"] > 1
