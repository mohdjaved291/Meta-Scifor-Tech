from django.urls import path
from .views import (
    DatabaseConnectionView,
    DatabaseSchemaView,
    QueryBuilderView,
    QueryExecutionView,
    QueryHistoryView,
    PerformanceAnalyticsView,
)

urlpatterns = [
    path("connections/", DatabaseConnectionView.as_view(), name="database-connections"),
    path(
        "connections/<int:connection_id>/schema/",
        DatabaseSchemaView.as_view(),
        name="database-schema",
    ),
    path("query/build/", QueryBuilderView.as_view(), name="query-builder"),
    path("query/execute/", QueryExecutionView.as_view(), name="query-execution"),
    path("query/history/", QueryHistoryView.as_view(), name="query-history"),
    path(
        "analytics/", PerformanceAnalyticsView.as_view(), name="performance-analytics"
    ),
]
