from rest_framework import serializers
from .models import User, Book, BorrowRecord


class UserSerializer(serializers.ModelSerializer):
    borrow_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "membership_date", "borrow_count"]
        read_only_fields = ["id", "membership_date"]

    def get_borrow_count(self, obj):
        return obj.borrow_records.filter(returned=False).count()


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "publication_year",
            "available_copies",
            "is_available",
        ]
        read_only_fields = ["id"]

    def get_is_available(self, obj):
        return obj.available_copies > 0


class BorrowRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = BorrowRecord
        fields = [
            "id",
            "user",
            "book",
            "user_name",
            "user_email",
            "book_title",
            "borrow_date",
            "return_date",
            "returned",
        ]
        read_only_fields = ["id", "borrow_date"]
