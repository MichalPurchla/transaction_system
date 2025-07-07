from django.contrib import admin
from django.urls import URLPattern, include, path

urlpatterns: list[URLPattern] = [
    path("admin/", admin.site.urls),
    path("transactions/", include("transactions.urls")),
    path("reports/", include("reports.urls")),
]
