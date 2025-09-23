"""
Views for Visual Database Query Builder - Minimal Working Version
"""

from __future__ import annotations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
import json
import hashlib
import time
from typing import Dict, List, Any

# Correct imports
from .models import DatabaseConnection, QueryHistory, PerformanceMetrics
from .serializers import DatabaseConnectionSerializer, QueryHistorySerializer
from .query_analyzer import QueryAnalyzer
from .performance_predictor import PerformancePredictor
from .database_connector import DatabaseConnector


class DatabaseConnectionView(APIView):
    def get(self, request):
        connections = DatabaseConnection.objects.all()
        serializer = DatabaseConnectionSerializer(connections, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DatabaseConnectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DatabaseSchemaView(APIView):
    def get(self, request, connection_id):
        try:
            connection = DatabaseConnection.objects.get(id=connection_id)
            connector = DatabaseConnector(
                {
                    "engine": connection.engine,
                    "host": connection.host,
                    "port": connection.port,
                    "database": connection.database,
                    "username": connection.username,
                    "password": connection.password,
                }
            )

            if connector.connect():
                schema = connector.get_schema()
                connector.close()

                # Simple schema response
                enhanced_schema = {}
                for table_name, columns in schema.items():
                    enhanced_schema[table_name] = {
                        "columns": columns,
                        "stats": {
                            "record_count": 1000,  # Default estimate
                            "table_size": "Unknown",
                            "indexes": [],
                            "has_indexes": False,
                        },
                    }

                database_overview = {
                    "total_tables": len(schema),
                    "total_records": len(schema) * 1000,  # Estimate
                    "relationships": [],
                    "performance_insights": ["Database schema loaded successfully"],
                }

                return Response(
                    {
                        "schema": enhanced_schema,
                        "overview": database_overview,
                        "relationships": [],
                    }
                )
            else:
                return Response(
                    {"error": "Failed to connect to database"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except DatabaseConnection.DoesNotExist:
            return Response(
                {"error": "Database connection not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class QueryBuilderView(APIView):
    def __init__(self):
        super().__init__()
        self.analyzer = QueryAnalyzer()
        self.predictor = PerformancePredictor()

    def post(self, request):
        try:
            data = request.data
            visual_query = data.get("visual_query", {})
            sql_query = data.get("sql_query", "")
            connection_id = data.get("connection_id")

            if not sql_query:
                sql_query = self._convert_visual_to_sql(visual_query)

            # Get database connection
            connection = DatabaseConnection.objects.get(id=connection_id)

            # Analyze query
            analysis = self.analyzer.analyze_query(sql_query)

            # Predict performance
            prediction = self.predictor.predict(analysis)

            response_data = {
                "sql_query": sql_query,
                "analysis": analysis,
                "prediction": prediction,
                "optimization_suggestions": analysis.get(
                    "optimization_suggestions", []
                ),
                "connection": {
                    "name": connection.name,
                    "database": connection.database,
                },
                "query_hash": hashlib.md5(sql_query.encode()).hexdigest(),
            }

            return Response(response_data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _convert_visual_to_sql(self, visual_query: Dict) -> str:
        """Convert visual query representation to SQL"""
        if not visual_query:
            return "SELECT * FROM table_name LIMIT 10"

        # Extract components
        tables = visual_query.get("tables", [])
        columns = visual_query.get("columns", ["*"])
        joins = visual_query.get("joins", [])
        where_conditions = visual_query.get("where", [])
        group_by = visual_query.get("groupBy", [])
        order_by = visual_query.get("orderBy", [])
        limit = visual_query.get("limit", None)

        # Build SQL query
        sql_parts = []

        # SELECT clause
        if columns:
            sql_parts.append(f"SELECT {', '.join(columns)}")
        else:
            sql_parts.append("SELECT *")

        # FROM clause
        if tables:
            sql_parts.append(f"FROM {tables[0]}")

        # JOIN clauses
        for join in joins:
            join_type = join.get("type", "INNER")
            table = join.get("table", "")
            condition = join.get("condition", "")
            sql_parts.append(f"{join_type} JOIN {table} ON {condition}")

        # WHERE clause
        if where_conditions:
            conditions = []
            for condition in where_conditions:
                column = condition.get("column", "")
                operator = condition.get("operator", "=")
                value = condition.get("value", "")
                if isinstance(value, str):
                    value = f"'{value}'"
                conditions.append(f"{column} {operator} {value}")
            sql_parts.append(f"WHERE {' AND '.join(conditions)}")

        # GROUP BY clause
        if group_by:
            sql_parts.append(f"GROUP BY {', '.join(group_by)}")

        # ORDER BY clause
        if order_by:
            order_clauses = []
            for order in order_by:
                column = order.get("column", "")
                direction = order.get("direction", "ASC")
                order_clauses.append(f"{column} {direction}")
            sql_parts.append(f"ORDER BY {', '.join(order_clauses)}")

        # LIMIT clause
        if limit:
            sql_parts.append(f"LIMIT {limit}")

        return " ".join(sql_parts)


class QueryExecutionView(APIView):
    def post(self, request):
        try:
            data = request.data
            sql_query = data.get("sql_query", "")
            connection_id = data.get("connection_id")
            visual_query = data.get("visual_query", {})

            # Get database connection
            connection = DatabaseConnection.objects.get(id=connection_id)
            connector = DatabaseConnector(
                {
                    "engine": connection.engine,
                    "host": connection.host,
                    "port": connection.port,
                    "database": connection.database,
                    "username": connection.username,
                    "password": connection.password,
                }
            )

            if not connector.connect():
                return Response(
                    {"error": "Failed to connect to database"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Execute query
            results, execution_time = connector.execute_query(sql_query)
            connector.close()

            # Analyze query for performance metrics
            analyzer = QueryAnalyzer()
            analysis = analyzer.analyze_query(sql_query)

            # Save to history
            user = request.user if request.user.is_authenticated else None
            if user:
                QueryHistory.objects.create(
                    user=user,
                    database=connection,
                    query=sql_query,
                    visual_query=visual_query,
                    execution_time=execution_time,
                    rows_returned=len(results),
                    optimization_suggestions=analysis.get(
                        "optimization_suggestions", []
                    ),
                )

            return Response(
                {
                    "results": results,
                    "execution_time": execution_time,
                    "rows_returned": len(results),
                    "analysis": analysis,
                    "performance_insights": [
                        f"Query executed in {execution_time:.3f} seconds",
                        f"Returned {len(results)} rows",
                    ],
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class QueryHistoryView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            history = QueryHistory.objects.filter(user=request.user)[:50]
            serializer = QueryHistorySerializer(history, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED
        )


class PerformanceAnalyticsView(APIView):
    def get(self, request):
        try:
            from django.db import models

            metrics = PerformanceMetrics.objects.all()

            analytics = {
                "total_queries": metrics.count(),
                "average_execution_time": metrics.aggregate(
                    models.Avg("execution_time")
                )["execution_time__avg"]
                or 0,
                "slowest_queries": list(
                    metrics.order_by("-execution_time")[:10].values(
                        "query_hash", "execution_time", "table_name"
                    )
                ),
                "most_used_tables": [],
            }

            return Response(analytics)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RealTimeAnalysisView(APIView):
    """Endpoint for real-time query analysis as user builds the query"""

    def post(self, request):
        try:
            data = request.data
            visual_query = data.get("visual_query", {})
            connection_id = data.get("connection_id")

            if not connection_id:
                return Response({"error": "Connection ID required"}, status=400)

            # Convert visual query to SQL for analysis
            query_builder = QueryBuilderView()
            sql_query = (
                query_builder._convert_visual_to_sql(visual_query)
                if visual_query
                else ""
            )

            if not sql_query or sql_query.strip() == "":
                return Response(
                    {
                        "status": "incomplete",
                        "message": "Query not ready for analysis",
                        "suggestions": [
                            "Add tables to FROM clause",
                            "Select columns to query",
                        ],
                    }
                )

            # Perform analysis
            analyzer = QueryAnalyzer()
            analysis = analyzer.analyze_query(sql_query)

            # Performance prediction
            predictor = PerformancePredictor()
            prediction = predictor.predict(analysis)

            return Response(
                {
                    "status": "ready",
                    "sql_preview": sql_query,
                    "analysis": {
                        "complexity_score": analysis["complexity_score"],
                        "table_count": len(analysis.get("tables", [])),
                        "join_count": analysis.get("joins", 0),
                        "condition_count": len(visual_query.get("where", [])),
                    },
                    "prediction": {
                        "estimated_time": prediction["predicted_time"],
                        "confidence": prediction["confidence"],
                        "category": prediction["performance_category"],
                        "memory_estimate": "5.0 MB",  # Default estimate
                    },
                    "instant_suggestions": [
                        (
                            "Query looks good!"
                            if analysis["complexity_score"] < 5
                            else "Consider optimizing complex query"
                        )
                    ],
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)
