from django.urls import path

from . import views

app_name = "donations"

urlpatterns = [
    path("", views.DonationView.as_view(), name="index"),
]
