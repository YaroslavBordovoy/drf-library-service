from rest_framework import generics
from books_service.models import Book
from books_service.paginations import BooksPagination
from books_service.serializers import BookListSerializer, BookDetailSerializer
from books_service.permissions import IsAdminOrReadOnly

class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)


class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    pagination_class = BooksPagination
    permission_classes = (IsAdminOrReadOnly,)


class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)


class BookUpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)



class BookDeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)
