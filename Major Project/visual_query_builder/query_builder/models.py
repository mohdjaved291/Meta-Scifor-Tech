from django.db import models
from django.contrib.auth.models import User
import json


class DatabaseConnection(models.Model):
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=5432)
    database = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    engine = models.CharField(
        max_length=50,
        choices=[
            ("postgresql", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("sqlite", "SQLite"),
            ("oracle", "Oracle"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class QueryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    database = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE)
    query = models.TextField()
    visual_query = models.JSONField(default=dict)
    execution_time = models.FloatField(null=True, blank=True)
    rows_returned = models.IntegerField(null=True, blank=True)
    predicted_time = models.FloatField(null=True, blank=True)
    actual_time = models.FloatField(null=True, blank=True)
    optimization_suggestions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PerformanceMetrics(models.Model):
    query_hash = models.CharField(max_length=64, db_index=True)
    table_name = models.CharField(max_length=100)
    operation_type = models.CharField(max_length=20)
    row_count = models.BigIntegerField()
    execution_time = models.FloatField()
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    io_reads = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
