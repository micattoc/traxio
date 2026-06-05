from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.generate_report, name="generate"),
    path("reports/save/", views.save_report, name="save"),
    path("history/", views.history, name="history"),
    path("reports/<int:pk>/", views.report_detail, name="detail"),
]