from logging import getLogger

from django.db.models import Max, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from reports.utils import parse_date_range
from transactions.models import Customer, Product, Transaction

logger = getLogger(__name__)

EXCHANGE_RATES = {
    "PLN": 1,
    "EUR": 4.3,
    "USD": 4.0,
}


@require_GET
def customer_summary(request, customer_id):
    """
    Returns a transaction summary for a given customer within an optional date range.

    Query Parameters:
        from (str, optional): Start date in YYYY-MM-DD or ISO 8601 format.
        to (str, optional): End date in YYYY-MM-DD or ISO 8601 format.

    Responses:
        200 OK:
            {
                "customer_id": str,
                "total_spent_pln": float,
                "unique_products": int,
                "last_transaction_date": str | null (ISO 8601)
            }
        404 Not Found:
            Returned if the customer with the given ID does not exist.
    """
    customer = get_object_or_404(Customer, id=customer_id)

    from_date, to_date = parse_date_range(request)
    transactions = Transaction.objects.filter(customer=customer)

    if from_date:
        transactions = transactions.filter(timestamp__date__gte=from_date)
    if to_date:
        transactions = transactions.filter(timestamp__date__lte=to_date)

    if not transactions.exists():
        return JsonResponse(
            {
                "customer_id": str(customer_id),
                "total_spent_pln": 0,
                "unique_products": 0,
                "last_transaction_date": None,
            }
        )

    total_spent = 0
    for t in transactions:
        rate = EXCHANGE_RATES.get(t.currency, 1)
        total_spent += float(t.amount) * rate

    unique_products = transactions.values("product").distinct().count()
    last_transaction_date = transactions.aggregate(last=Max("timestamp"))["last"]

    return JsonResponse(
        {
            "customer_id": str(customer_id),
            "total_spent_pln": round(total_spent, 2),
            "unique_products": unique_products,
            "last_transaction_date": last_transaction_date,
        }
    )


@require_GET
def product_summary(request, product_id):
    """
    Returns a transaction summary for a given product within an optional date range.

    Query Parameters:
        from (str, optional): Start date in YYYY-MM-DD or ISO 8601 format.
        to (str, optional): End date in YYYY-MM-DD or ISO 8601 format.

    Responses:
        200 OK:
            {
                "product_id": str,
                "total_quantity_sold": int,
                "total_revenue_pln": float,
                "unique_customers": int
            }
        404 Not Found:
            Returned if the product with the given ID does not exist.
    """
    product = get_object_or_404(Product, id=product_id)

    from_date, to_date = parse_date_range(request)
    transactions = Transaction.objects.filter(product=product)

    if from_date:
        transactions = transactions.filter(timestamp__date__gte=from_date)
    if to_date:
        transactions = transactions.filter(timestamp__date__lte=to_date)

    if not transactions.exists():
        return JsonResponse(
            {
                "product_id": str(product_id),
                "total_quantity_sold": 0,
                "total_revenue_pln": 0,
                "unique_customers": 0,
            }
        )

    total_quantity = transactions.aggregate(total=Sum("quantity"))["total"] or 0

    total_revenue = 0
    for t in transactions:
        rate = EXCHANGE_RATES.get(t.currency, 1)
        total_revenue += float(t.amount) * rate

    unique_customers = transactions.values("customer").distinct().count()

    return JsonResponse(
        {
            "product_id": str(product_id),
            "total_quantity_sold": total_quantity,
            "total_revenue_pln": round(total_revenue, 2),
            "unique_customers": unique_customers,
        }
    )
