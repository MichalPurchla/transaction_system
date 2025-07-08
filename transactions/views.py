import csv
import io
import uuid
from datetime import datetime
from logging import getLogger

from django.http import Http404, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from transactions.models import Customer, Product, Transaction

logger = getLogger(__name__)


class TransactionListView(ListView):
    """
    Returns a paginated list of transactions with optional filtering.

    Query Parameters:
        customer_id (str, optional): UUID of the customer to filter transactions.
        product_id (str, optional): UUID of the product to filter transactions.
        page (int, optional): Page number for pagination.

    Pagination:
        Default page size: 50 transactions per page.

    Response (200 OK):
        {
            "count": int,
            "num_pages": int,
            "current_page": int,
            "has_next": bool,
            "has_previous": bool,
            "transactions": [
                {
                    "transaction_id": str,
                    "timestamp": str (ISO 8601),
                    "amount": str,
                    "currency": str,
                    "customer_id": str,
                    "product_id": str,
                    "quantity": int
                },
                ...
            ]
        }
    """

    model = Transaction
    paginate_by = 50

    def get_queryset(self):
        queryset = Transaction.objects.all().order_by("-timestamp")

        if customer_id := self.request.GET.get("customer_id"):
            queryset = queryset.filter(customer__id=customer_id)
        if product_id := self.request.GET.get("product_id"):
            queryset = queryset.filter(product__id=product_id)

        return queryset

    def render_to_response(self, context, **response_kwargs):
        page = context["page_obj"]
        data = {
            "count": page.paginator.count,
            "num_pages": page.paginator.num_pages,
            "current_page": page.number,
            "has_next": page.has_next(),
            "has_previous": page.has_previous(),
            "transactions": [
                {
                    "transaction_id": str(obj.transaction_id),
                    "timestamp": obj.timestamp.isoformat(),
                    "amount": str(obj.amount),
                    "currency": obj.currency,
                    "customer_id": str(obj.customer.id),
                    "product_id": str(obj.product.id),
                    "quantity": obj.quantity,
                }
                for obj in page.object_list
            ],
        }
        return JsonResponse(data, **response_kwargs)


class TransactionDetailView(View):
    """
    Returns the details of a single transaction by its UUID.

    Path Parameters:
        transaction_id (str): UUID of the transaction.

    Response (200 OK):
        {
            "transaction_id": str,
            "timestamp": str (ISO 8601),
            "amount": str,
            "currency": str,
            "customer_id": str,
            "product_id": str,
            "quantity": int
        }

    Response (404 Not Found):
        Returned if the transaction with the specified UUID does not exist.
    """

    def get(self, request, *args, **kwargs):
        transaction_id = kwargs["transaction_id"]
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
        except Transaction.DoesNotExist:
            logger.warning(f"Transaction with id={transaction_id} not found")
            raise Http404("Transaction not found")

        data = {
            "transaction_id": str(transaction.transaction_id),
            "timestamp": transaction.timestamp.isoformat(),
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "customer_id": str(transaction.customer.id),
            "product_id": str(transaction.product.id),
            "quantity": transaction.quantity,
        }
        return JsonResponse(data)


@csrf_exempt
@require_POST
def upload_transactions_csv(request):
    """
    Uploads a CSV file to bulk create transactions in the system.

    Request:
        Multipart form-data with a single field:
            file: CSV file containing transaction data.

    CSV Format:
        The CSV must contain the following headers:
            - transaction_id
            - timestamp (ISO 8601)
            - amount
            - currency
            - customer_id
            - product_id
            - quantity

    Response (201 Created):
        {
            "inserted": int,        # Number of successfully inserted transactions
            "errors": [
                {
                    "line": int,
                    "row": dict,
                    "error": str
                },
                ...
            ]
        }

    Response (400 Bad Request):
        {
            "error": "No file provided."
        }
        or
        {
            "error": "File is not CSV."
        }

    Notes:
        - Each valid row in the CSV will be inserted as a `Transaction` record.
        - Rows with errors will be logged and returned in the `errors` array with details.
        - CSV processing continues even if some rows fail, inserting as many valid rows as possible.
    """
    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided."}, status=400)

    csv_file = request.FILES["file"]
    if not csv_file.name.endswith(".csv"):
        return JsonResponse({"error": "File is not CSV."}, status=400)

    decoded_file = csv_file.read().decode("utf-8")
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)

    transactions_inserted = 0
    errors = []
    line_number = 1

    for row in reader:
        line_number += 1
        try:
            transaction_id = uuid.UUID(row["transaction_id"])
            timestamp = datetime.fromisoformat(row["timestamp"])
            amount = float(row["amount"])
            currency = row["currency"].strip().upper()
            customer_id = uuid.UUID(row["customer_id"])
            product_id = uuid.UUID(row["product_id"])
            quantity = int(row["quantity"])

            Transaction.objects.create(
                transaction_id=transaction_id,
                timestamp=timestamp,
                amount=amount,
                currency=currency,
                customer=Customer.objects.get(id=customer_id),
                product=Product.objects.get(id=product_id),
                quantity=quantity,
            )
            transactions_inserted += 1
        except Exception as e:
            errors.append({"line": line_number, "row": row, "error": str(e)})
            logger.error(f"Błąd podczas przetwarzania CSV w linii {line_number} | row={row} | error={e}")

    return JsonResponse({"inserted": transactions_inserted, "errors": errors}, status=201)
