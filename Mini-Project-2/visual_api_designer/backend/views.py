from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import User, Book, BorrowRecord
from .serializers import UserSerializer, BookSerializer, BorrowRecordSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=["get"])
    def borrowed_books(self, request, pk=None):
        """Get all books currently borrowed by this user"""
        user = self.get_object()
        records = BorrowRecord.objects.filter(user=user, returned=False)
        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def borrow_history(self, request, pk=None):
        """Get complete borrowing history for this user"""
        user = self.get_object()
        records = BorrowRecord.objects.filter(user=user).order_by("-borrow_date")
        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=True, methods=["post"])
    def borrow(self, request, pk=None):
        """Borrow a book"""
        book = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if book is available
        if book.available_copies <= 0:
            return Response(
                {"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already has this book
        existing_borrow = BorrowRecord.objects.filter(
            user=user, book=book, returned=False
        ).exists()

        if existing_borrow:
            return Response(
                {"error": "User has already borrowed this book"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create borrow record
        record = BorrowRecord.objects.create(user=user, book=book)
        book.available_copies -= 1
        book.save()

        return Response(
            BorrowRecordSerializer(record).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        """Return a borrowed book"""
        book = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            record = BorrowRecord.objects.get(
                user_id=user_id, book=book, returned=False
            )
        except BorrowRecord.DoesNotExist:
            return Response(
                {"error": "No active borrow record found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return the book
        record.returned = True
        record.return_date = timezone.now()
        record.save()

        book.available_copies += 1
        book.save()

        return Response(BorrowRecordSerializer(record).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def available(self, request):
        """Get all available books"""
        books = Book.objects.filter(available_copies__gt=0)
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)


class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """Get overdue books (borrowed more than 30 days ago)"""
        from datetime import timedelta

        thirty_days_ago = timezone.now() - timedelta(days=30)

        overdue_records = BorrowRecord.objects.filter(
            returned=False, borrow_date__lt=thirty_days_ago
        )
        serializer = self.get_serializer(overdue_records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get all active (not returned) borrow records"""
        active_records = BorrowRecord.objects.filter(returned=False)
        serializer = self.get_serializer(active_records, many=True)
        return Response(serializer.data)
