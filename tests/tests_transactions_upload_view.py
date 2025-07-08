import csv
import io
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from uuid import uuid4

import pytest
from django.urls import reverse

from transactions.models import Customer, Product, Transaction


@pytest.mark.django_db
class TestUploadTransactionsCSV:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("upload_transactions_csv")
        self.customer = Customer.objects.create(id=uuid4(), name="Test Customer", email="test@example.com")
        self.product = Product.objects.create(id=uuid4(), name="Test Product", description="Test Description")

    def create_csv_file(self, rows):
        output = io.StringIO()
        fieldnames = ["transaction_id", "timestamp", "amount", "currency", "customer_id", "product_id", "quantity"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        output.seek(0)
        return output

    def test_upload_no_file(self, auth_client):
        response = auth_client.post(self.url)
        assert response.status_code == 400
        assert response.json()["error"] == "No file provided."

    def test_upload_not_csv(self, auth_client):
        file = BytesIO(b"not a csv")
        file.name = "test.txt"
        response = auth_client.post(self.url, {"file": file})
        assert response.status_code == 400
        assert response.json()["error"] == "File is not CSV."

    def test_upload_valid_csv(self, auth_client):
        transaction_id = uuid4()
        timestamp = datetime.now().isoformat()
        row = {
            "transaction_id": str(transaction_id),
            "timestamp": timestamp,
            "amount": "123.45",
            "currency": "USD",
            "customer_id": str(self.customer.id),
            "product_id": str(self.product.id),
            "quantity": "2",
        }
        csv_file = self.create_csv_file([row])
        csv_file.name = "transactions.csv"

        response = auth_client.post(self.url, {"file": csv_file})
        assert response.status_code == 201
        data = response.json()
        assert data["inserted"] == 1
        assert data["errors"] == []

        transaction = Transaction.objects.get(transaction_id=transaction_id)
        assert transaction.amount == Decimal("123.45")
        assert transaction.currency == "USD"
        assert transaction.customer == self.customer
        assert transaction.product == self.product
        assert transaction.quantity == 2

    def test_upload_csv_with_invalid_customer(self, auth_client):
        transaction_id = uuid4()
        timestamp = datetime.now().isoformat()
        row = {
            "transaction_id": str(transaction_id),
            "timestamp": timestamp,
            "amount": "123.45",
            "currency": "USD",
            "customer_id": str(uuid4()),
            "product_id": str(self.product.id),
            "quantity": "2",
        }
        csv_file = self.create_csv_file([row])
        csv_file.name = "transactions.csv"

        response = auth_client.post(self.url, {"file": csv_file})
        assert response.status_code == 201
        data = response.json()
        assert data["inserted"] == 0
        assert len(data["errors"]) == 1
