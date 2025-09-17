from django.contrib import admin
from .models import User, Book, BorrowRecord


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "membership_date", "active_borrows_count"]
    list_filter = ["membership_date"]
    search_fields = ["email", "full_name"]
    readonly_fields = ["membership_date"]

    def active_borrows_count(self, obj):
        return obj.borrow_records.filter(returned=False).count()

    active_borrows_count.short_description = "Active Borrows"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "isbn",
        "publication_year",
        "available_copies",
        "total_borrows",
    ]
    list_filter = ["publication_year", "author"]
    search_fields = ["title", "author", "isbn"]

    def total_borrows(self, obj):
        return obj.borrow_records.count()

    total_borrows.short_description = "Total Borrows"


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "book",
        "borrow_date",
        "return_date",
        "returned",
        "is_overdue",
    ]
    list_filter = ["returned", "borrow_date", "return_date"]
    search_fields = ["user__email", "user__full_name", "book__title"]
    readonly_fields = ["borrow_date"]

    def is_overdue(self, obj):
        if obj.returned:
            return False
        from django.utils import timezone
        from datetime import timedelta

        return timezone.now() > obj.borrow_date + timedelta(days=30)

    is_overdue.boolean = True
    is_overdue.short_description = "Overdue"
