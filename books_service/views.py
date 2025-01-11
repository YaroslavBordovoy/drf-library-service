from rest_framework import generics
from .models import Book
from .paginations import BooksPagination
from .serializers import BookListSerializer, BookDetailSerializer
from .permissions import IsAdminOrReadOnly


class BaseBookPermissionView:
    # permission_classes = IsAdminOrReadOnly
    pass


class BookCreateView(generics.CreateAPIView, BaseBookPermissionView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)


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
    permission_classes = (IsAdminOrReadOnly,)



class BookDeleteView(generics.DestroyAPIView, BaseBookPermissionView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)

