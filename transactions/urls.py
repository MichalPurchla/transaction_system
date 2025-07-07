from django.urls import URLPattern, path

from .views import TransactionDetailView, TransactionListView, upload_transactions_csv

urlpatterns: list[URLPattern] = [
    path("upload/", upload_transactions_csv, name="upload_transactions_csv"),
    path("", TransactionListView.as_view(), name="transactions_list"),
    path("<uuid:transaction_id>/", TransactionDetailView.as_view(), name="transaction_detail"),
]
