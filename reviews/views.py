# reviews/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Review


class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "reviews/review_list.html"
    context_object_name = "reviews"


class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = Review
    template_name = "reviews/review_detail.html"
    context_object_name = "review"


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ["title", "content", "rating"]
    template_name = "reviews/review_form.html"
    success_url = reverse_lazy("reviews:review-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    fields = ["title", "content", "rating"]
    template_name = "reviews/review_form.html"
    success_url = reverse_lazy("reviews:review-list")


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "reviews/review_confirm_delete.html"
    success_url = reverse_lazy("reviews:review-list")
