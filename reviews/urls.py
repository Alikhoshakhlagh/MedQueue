from django.urls import path
from .views import (
    ReviewListView, ReviewDetailView,
    ReviewCreateView, ReviewUpdateView, ReviewDeleteView
)

app_name = "reviews"

urlpatterns = [
    path("", ReviewListView.as_view(), name="review-list"),
    path("<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
    path("create/", ReviewCreateView.as_view(), name="review-create"),
    path("<int:pk>/edit/", ReviewUpdateView.as_view(), name="review-edit"),
    path("<int:pk>/delete/", ReviewDeleteView.as_view(), name="review-delete"),
]