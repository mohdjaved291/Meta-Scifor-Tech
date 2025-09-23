"""
Django Admin Configuration for Visual Database Query Builder
"""

from django.contrib import admin
from .models import DatabaseConnection, QueryHistory, PerformanceMetrics


@admin.register(DatabaseConnection)
class DatabaseConnectionAdmin(admin.ModelAdmin):
    list_display = ("name", "engine", "host", "database", "created_at")
    list_filter = ("engine", "created_at")
    search_fields = ("name", "host", "database")
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Information", {"fields": ("name", "engine")}),
        (
            "Connection Details",
            {"fields": ("host", "port", "database", "username", "password")},
        ),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make password field use password input widget
        if "password" in form.base_fields:
            form.base_fields["password"].widget.attrs["type"] = "password"
        return form


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "database", "execution_time", "rows_returned", "created_at")
    list_filter = ("database", "created_at")
    search_fields = ("user__username", "query")
    readonly_fields = (
        "created_at",
    )  # Removed query_hash as it doesn't exist in the model
    date_hierarchy = "created_at"

    fieldsets = (
        ("Query Information", {"fields": ("user", "database", "query")}),
        (
            "Performance Metrics",
            {
                "fields": (
                    "execution_time",
                    "rows_returned",
                    "predicted_time",
                    "actual_time",
                )
            },
        ),
        (
            "Analysis",
            {
                "fields": ("visual_query", "optimization_suggestions"),
                "classes": ("collapse",),
            },
        ),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        # Make all fields readonly when viewing existing objects
        if obj:
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields


@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "table_name",
        "operation_type",
        "execution_time",
        "row_count",
        "created_at",
    )
    list_filter = ("operation_type", "created_at")
    search_fields = ("table_name", "query_hash")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Query Information",
            {"fields": ("query_hash", "table_name", "operation_type")},
        ),
        (
            "Performance Data",
            {
                "fields": (
                    "row_count",
                    "execution_time",
                    "cpu_usage",
                    "memory_usage",
                    "io_reads",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        # Make all fields readonly when viewing existing objects
        if obj:
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields


# Optional: Customize admin site headers
admin.site.site_header = "Visual Database Query Builder Admin"
admin.site.site_title = "Query Builder Admin"
admin.site.index_title = "Welcome to Query Builder Administration"
