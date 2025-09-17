from django.contrib import admin
from django.utils.html import format_html
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Post model with image support
    """

    list_display = [
        "title",
        "image_preview",  # Add image preview to list
        "category_badge",
        "is_published",
        "view_count",
        "reading_time_display",
        "created_at",
        "updated_at",
    ]

    list_filter = ["category", "is_published", "created_at", "updated_at"]

    search_fields = ["title", "content", "excerpt"]

    readonly_fields = [
        "view_count",
        "created_at",
        "updated_at",
        "reading_time_display",
        "image_preview_large",
    ]

    fieldsets = (
        ("Basic Information", {"fields": ("title", "category", "is_published")}),
        (
            "Content",
            {
                "fields": ("content", "excerpt"),
                "description": "The main content of your blog post",
            },
        ),
        (
            "Image",
            {
                "fields": ("image", "image_preview_large"),
                "description": "Upload an image for your blog post",
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "view_count",
                    "reading_time_display",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
                "description": "Automatically generated information",
            },
        ),
    )

    list_per_page = 25
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    actions = ["make_published", "make_unpublished", "reset_view_count"]

    def image_preview(self, obj):
        """Small image preview for list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Image"

    def image_preview_large(self, obj):
        """Large image preview for detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;" />',
                obj.image.url,
            )
        return "No image uploaded"

    image_preview_large.short_description = "Current Image"

    def category_badge(self, obj):
        """Display category with colored badge"""
        colors = {
            "tech": "#3b82f6",
            "design": "#e91e63",
            "lifestyle": "#10b981",
            "education": "#f59e0b",
            "business": "#ef4444",
            "entertainment": "#8b5cf6",
            "other": "#6b7280",
        }
        color = colors.get(obj.category, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 10px; font-size: 12px;">{}</span>',
            color,
            obj.get_category_display(),
        )

    category_badge.short_description = "Category"

    def reading_time_display(self, obj):
        """Display reading time with icon"""
        return format_html(
            '<span title="Estimated reading time">📖 {} min</span>', obj.reading_time
        )

    reading_time_display.short_description = "Reading Time"

    def make_published(self, request, queryset):
        """Custom action to publish posts"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} post(s) were successfully published.")

    make_published.short_description = "Publish selected posts"

    def make_unpublished(self, request, queryset):
        """Custom action to unpublish posts"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} post(s) were successfully unpublished.")

    make_unpublished.short_description = "Unpublish selected posts"

    def reset_view_count(self, request, queryset):
        """Custom action to reset view counts"""
        updated = queryset.update(view_count=0)
        self.message_user(request, f"View count reset for {updated} post(s).")

    reset_view_count.short_description = "Reset view count"

    def get_queryset(self, request):
        """Optimize queries for admin interface"""
        return super().get_queryset(request).select_related()
