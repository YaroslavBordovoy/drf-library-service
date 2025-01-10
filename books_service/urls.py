from django.urls import path
from books_service.views import (
    BookCreateView,
    BookListView,
    BookDetailView,
    BookUpdateView,
    BookDeleteView,
)

app_name = "book"

urlpatterns = [
    path("", BookListView.as_view(), name="book-list"),
    path("<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("create/", BookCreateView.as_view(), name="book-create"),
    path(
        "<int:pk>/update/", BookUpdateView.as_view(), name="book-update"
    ),
    path(
        "<int:pk>/delete/", BookDeleteView.as_view(), name="book-delete"
    ),
]
