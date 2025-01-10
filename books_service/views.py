from rest_framework import generics
from books_service.models import Book
from books_service.paginations import BooksPagination
from books_service.serializers import BookListSerializer, BookDetailSerializer
# from books_service.permissions import IsAdminOrReadOnly


class BaseBookPermissionView:
    # permission_classes = IsAdminOrReadOnly
    pass


class BookCreateView(generics.CreateAPIView, BaseBookPermissionView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer


class BookListView(generics.ListAPIView, BaseBookPermissionView):
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    pagination_class = BooksPagination


class BookDetailView(generics.RetrieveAPIView, BaseBookPermissionView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer


class BookUpdateView(generics.UpdateAPIView, BaseBookPermissionView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer


class BookDeleteView(generics.DestroyAPIView, BaseBookPermissionView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
