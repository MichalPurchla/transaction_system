from django.urls import URLPattern, path

from .views import customer_summary, product_summary

urlpatterns: list[URLPattern] = [
    path("customer-summary/<uuid:customer_id>/", customer_summary, name="customer_summary"),
    path("product-summary/<uuid:product_id>/", product_summary, name="product_summary"),
]
