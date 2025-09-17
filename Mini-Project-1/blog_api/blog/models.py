from django.db import models


class Post(models.Model):
    """
    Enhanced blog post model with modern features
    """

    CATEGORY_CHOICES = [
        ("tech", "Technology"),
        ("design", "Design"),
        ("business", "Business"),
        ("lifestyle", "Lifestyle"),
        ("education", "Education"),
        ("entertainment", "Entertainment"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="tech")
    excerpt = models.TextField(max_length=300, blank=True)
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.excerpt and self.content:
            self.excerpt = (
                self.content[:150] + "..." if len(self.content) > 150 else self.content
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def reading_time(self):
        words = len(self.content.split())
        minutes = max(1, round(words / 200))
        return f"{minutes} min read"

    @property
    def category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
