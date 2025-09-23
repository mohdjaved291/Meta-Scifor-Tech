from rest_framework import serializers
from .models import DatabaseConnection, QueryHistory, PerformanceMetrics


class DatabaseConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseConnection
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class QueryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryHistory
        fields = "__all__"


class PerformanceMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceMetrics
        fields = "__all__"
