from django.db import models

# Create your models here.


class User(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    membership_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.email)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255, unique=True)
    publication_year = models.IntegerField()
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.title)


class BorrowRecord(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    # Relationships
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="borrow_records"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrow_records"
    )

    class Meta:
        unique_together = [
            "user",
            "book",
            "returned",
        ]  # Prevent duplicate active borrows

    def __str__(self):
        return f"{self.user.full_name} borrowed {self.book.title}"
