from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Book
from .paginations import BooksPagination
from .serializers import BookListSerializer, BookDetailSerializer
from .permissions import IsAdminOrReadOnly


class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)


class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    pagination_class = BooksPagination
    permission_classes = (AllowAny,)


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
