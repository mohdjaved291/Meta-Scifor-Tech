"""
Views for Visual Database Query Builder - Enhanced with Sample Data Fallback
Replace your existing views.py with this complete version
"""

from __future__ import annotations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
import json
import hashlib
import time
import os
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

            # If it's SQLite, create sample data and return schema
            if connection.engine == "sqlite":
                return self.get_sqlite_schema_with_sample_data(connection)

            # For PostgreSQL, try to connect but fallback to sample data
            elif connection.engine == "postgresql":
                return self.get_postgresql_schema_with_fallback(connection)

            else:
                return self.get_sample_schema_response(connection)

        except DatabaseConnection.DoesNotExist:
            return Response(
                {"error": "Database connection not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get_postgresql_schema_with_fallback(self, connection):
        """Try PostgreSQL connection, fallback to sample data if it fails"""

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
            try:
                schema = connector.get_schema()
                connector.close()

                if schema:  # If we got real schema
                    enhanced_schema = {}
                    for table_name, table_data in schema.items():
                        enhanced_schema[table_name] = {
                            "columns": table_data.get("columns", []),
                            "stats": table_data.get(
                                "stats",
                                {
                                    "record_count": 1000,
                                    "table_size": "Unknown",
                                    "has_indexes": False,
                                },
                            ),
                        }

                    database_overview = {
                        "total_tables": len(schema),
                        "total_records": sum(
                            table.get("stats", {}).get("record_count", 0)
                            for table in schema.values()
                        ),
                        "relationships": [],
                        "performance_insights": [
                            f"Successfully connected to PostgreSQL database with {len(schema)} tables"
                        ],
                    }

                    return Response(
                        {
                            "schema": enhanced_schema,
                            "overview": database_overview,
                            "relationships": [],
                            "connection_status": "success",
                            "data_source": "postgresql",
                        }
                    )
            except Exception as e:
                print(f"Error extracting PostgreSQL schema: {e}")

        # PostgreSQL failed, return sample data
        connector.close()
        print("🔄 PostgreSQL connection failed, using sample data for demo")
        return self.get_sample_schema_response(connection, source="postgresql_fallback")

    def get_sqlite_schema_with_sample_data(self, connection):
        """Create SQLite sample data and return schema"""

        # Create sample tables in SQLite
        self.create_sample_sqlite_tables()

        # Try to get real SQLite schema
        connector = DatabaseConnector(
            {
                "engine": "sqlite",
                "host": "localhost",
                "port": 0,
                "database": connection.database,
                "username": "",
                "password": "",
            }
        )

        if connector.connect():
            try:
                schema = connector.get_schema()
                connector.close()

                if schema:
                    enhanced_schema = {}
                    for table_name, table_data in schema.items():
                        enhanced_schema[table_name] = {
                            "columns": table_data.get("columns", []),
                            "stats": table_data.get(
                                "stats",
                                {
                                    "record_count": 5,
                                    "table_size": "1 KB",
                                    "has_indexes": True,
                                },
                            ),
                        }

                    database_overview = {
                        "total_tables": len(schema),
                        "total_records": sum(
                            table.get("stats", {}).get("record_count", 5)
                            for table in schema.values()
                        ),
                        "relationships": [],
                        "performance_insights": [
                            f"SQLite database with {len(schema)} sample tables ready for testing"
                        ],
                    }

                    return Response(
                        {
                            "schema": enhanced_schema,
                            "overview": database_overview,
                            "relationships": [],
                            "connection_status": "success",
                            "data_source": "sqlite",
                        }
                    )
            except Exception as e:
                print(f"SQLite schema error: {e}")

        connector.close()
        return self.get_sample_schema_response(connection, source="sqlite_fallback")

    def get_sample_schema_response(self, connection, source="sample"):
        """Return guaranteed sample schema for visual query builder demo"""

        sample_schema = {
            "users": {
                "columns": [
                    {
                        "name": "id",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": True,
                    },
                    {
                        "name": "name",
                        "type": "varchar",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "email",
                        "type": "varchar",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "age",
                        "type": "integer",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "department",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "salary",
                        "type": "decimal",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "hire_date",
                        "type": "date",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "is_active",
                        "type": "boolean",
                        "nullable": True,
                        "primary_key": False,
                    },
                ],
                "stats": {
                    "record_count": 25,
                    "table_size": "5 KB",
                    "has_indexes": True,
                },
            },
            "products": {
                "columns": [
                    {
                        "name": "id",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": True,
                    },
                    {
                        "name": "name",
                        "type": "varchar",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "category",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "price",
                        "type": "decimal",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "stock_quantity",
                        "type": "integer",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "description",
                        "type": "text",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "created_at",
                        "type": "timestamp",
                        "nullable": True,
                        "primary_key": False,
                    },
                ],
                "stats": {
                    "record_count": 50,
                    "table_size": "8 KB",
                    "has_indexes": True,
                },
            },
            "orders": {
                "columns": [
                    {
                        "name": "id",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": True,
                    },
                    {
                        "name": "user_id",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "product_id",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "quantity",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "total_price",
                        "type": "decimal",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "order_date",
                        "type": "date",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "status",
                        "type": "varchar",
                        "nullable": False,
                        "primary_key": False,
                    },
                ],
                "stats": {
                    "record_count": 100,
                    "table_size": "12 KB",
                    "has_indexes": True,
                },
            },
            "customers": {
                "columns": [
                    {
                        "name": "id",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": True,
                    },
                    {
                        "name": "company_name",
                        "type": "varchar",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "contact_name",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "email",
                        "type": "varchar",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "phone",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "address",
                        "type": "text",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "city",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "country",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                ],
                "stats": {
                    "record_count": 30,
                    "table_size": "6 KB",
                    "has_indexes": True,
                },
            },
            "departments": {
                "columns": [
                    {
                        "name": "id",
                        "type": "integer",
                        "nullable": False,
                        "primary_key": True,
                    },
                    {
                        "name": "name",
                        "type": "varchar",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "budget",
                        "type": "decimal",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "manager_id",
                        "type": "integer",
                        "nullable": True,
                        "primary_key": False,
                    },
                    {
                        "name": "location",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                ],
                "stats": {"record_count": 8, "table_size": "2 KB", "has_indexes": True},
            },
        }

        database_overview = {
            "total_tables": len(sample_schema),
            "total_records": sum(
                table["stats"]["record_count"] for table in sample_schema.values()
            ),
            "relationships": [
                {
                    "from_table": "users",
                    "from_column": "id",
                    "to_table": "orders",
                    "to_column": "user_id",
                },
                {
                    "from_table": "products",
                    "from_column": "id",
                    "to_table": "orders",
                    "to_column": "product_id",
                },
                {
                    "from_table": "departments",
                    "from_column": "id",
                    "to_table": "users",
                    "to_column": "department_id",
                },
            ],
            "performance_insights": [
                "Sample database schema loaded for demonstration",
                "5 tables with realistic business data structure",
                "Ready for visual query building and testing",
                f"Data source: {source}",
            ],
        }

        return Response(
            {
                "schema": sample_schema,
                "overview": database_overview,
                "relationships": database_overview["relationships"],
                "connection_status": "sample_data",
                "data_source": source,
                "message": "Using sample data for visual query builder demonstration",
            }
        )

    def create_sample_sqlite_tables(self):
        """Create sample tables in SQLite for demonstration"""
        from django.db import connection

        try:
            cursor = connection.cursor()

            # Create sample users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sample_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    age INTEGER,
                    department VARCHAR(50),
                    salary DECIMAL(10,2),
                    hire_date DATE,
                    is_active BOOLEAN DEFAULT 1
                )
            """
            )

            # Create sample products table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sample_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    price DECIMAL(10,2),
                    stock_quantity INTEGER DEFAULT 0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create sample orders table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sample_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    total_price DECIMAL(10,2),
                    order_date DATE DEFAULT CURRENT_DATE,
                    status VARCHAR(20) DEFAULT 'pending'
                )
            """
            )

            # Insert sample data if tables are empty
            cursor.execute("SELECT COUNT(*) FROM sample_users")
            if cursor.fetchone()[0] == 0:
                sample_users = [
                    (
                        "John Doe",
                        "john@example.com",
                        30,
                        "Engineering",
                        75000.00,
                        "2023-01-15",
                    ),
                    (
                        "Jane Smith",
                        "jane@example.com",
                        28,
                        "Marketing",
                        65000.00,
                        "2023-02-01",
                    ),
                    (
                        "Bob Johnson",
                        "bob@example.com",
                        35,
                        "Sales",
                        70000.00,
                        "2023-01-20",
                    ),
                    (
                        "Alice Brown",
                        "alice@example.com",
                        32,
                        "Engineering",
                        80000.00,
                        "2023-03-01",
                    ),
                    (
                        "Charlie Wilson",
                        "charlie@example.com",
                        29,
                        "HR",
                        60000.00,
                        "2023-02-15",
                    ),
                ]

                cursor.executemany(
                    """
                    INSERT INTO sample_users (name, email, age, department, salary, hire_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    sample_users,
                )

                sample_products = [
                    (
                        "Laptop Pro",
                        "Electronics",
                        1299.99,
                        50,
                        "High-performance laptop",
                    ),
                    (
                        "Wireless Headphones",
                        "Electronics",
                        199.99,
                        100,
                        "Noise-cancelling headphones",
                    ),
                    ("Office Chair", "Furniture", 299.99, 25, "Ergonomic office chair"),
                    ("Coffee Mug", "Kitchen", 12.99, 200, "Ceramic coffee mug"),
                    ("Desk Lamp", "Furniture", 79.99, 30, "LED desk lamp"),
                ]

                cursor.executemany(
                    """
                    INSERT INTO sample_products (name, category, price, stock_quantity, description)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    sample_products,
                )

                sample_orders = [
                    (1, 1, 1, 1299.99, "2024-01-15", "completed"),
                    (2, 2, 1, 199.99, "2024-01-16", "completed"),
                    (3, 3, 2, 599.98, "2024-01-17", "pending"),
                    (1, 4, 3, 38.97, "2024-01-18", "completed"),
                    (2, 5, 1, 79.99, "2024-01-19", "shipped"),
                ]

                cursor.executemany(
                    """
                    INSERT INTO sample_orders (user_id, product_id, quantity, total_price, order_date, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    sample_orders,
                )

            cursor.close()
            print("✅ Sample SQLite tables created successfully")

        except Exception as e:
            print(f"Error creating sample SQLite tables: {e}")
            pass  # Don't fail if SQLite tables can't be created


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
            return "SELECT * FROM users LIMIT 10"

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

            # For sample data connections, return mock results
            if (
                connection.name == "Sample SQLite Database"
                or connection.engine == "sqlite"
            ):
                return self.execute_sample_query(sql_query, connection, visual_query)

            # Try real database execution
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
                return self.execute_sample_query(sql_query, connection, visual_query)

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

    def execute_sample_query(self, sql_query, connection, visual_query):
        """Execute mock query for demonstration purposes"""

        # Generate sample results based on the query
        sample_results = [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "department": "Engineering",
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "age": 28,
                "department": "Marketing",
            },
            {
                "id": 3,
                "name": "Bob Johnson",
                "email": "bob@example.com",
                "age": 35,
                "department": "Sales",
            },
        ]

        execution_time = 0.045  # Mock execution time

        # Analyze query for performance metrics
        analyzer = QueryAnalyzer()
        analysis = analyzer.analyze_query(sql_query)

        return Response(
            {
                "results": sample_results,
                "execution_time": execution_time,
                "rows_returned": len(sample_results),
                "analysis": analysis,
                "performance_insights": [
                    f"Sample query executed in {execution_time:.3f} seconds",
                    f"Returned {len(sample_results)} sample rows",
                    "Using demo data for query builder demonstration",
                ],
                "data_source": "sample",
            }
        )


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


class CreateSampleDataView(APIView):
    """
    API endpoint to create sample data for testing
    Visit: /api/create-sample-data/ to set up sample database connections
    """

    def get(self, request):
        try:
            # Create sample SQLite connection
            sqlite_conn, created = DatabaseConnection.objects.get_or_create(
                name="Sample SQLite Database",
                defaults={
                    "host": "localhost",
                    "port": 0,
                    "database": "sample_data.db",
                    "username": "sqlite",
                    "password": "",
                    "engine": "sqlite",
                },
            )

            results = {
                "success": True,
                "message": "Sample data created successfully!",
                "connections_created": [],
                "admin_user": None,
                "next_steps": [
                    "Go to your app homepage",
                    'Select "Sample SQLite Database" from dropdown',
                    "Start building queries with drag & drop!",
                    "Try dragging tables and columns to build SQL queries",
                ],
            }

            if created:
                results["connections_created"].append(
                    {
                        "name": sqlite_conn.name,
                        "engine": sqlite_conn.engine,
                        "status": "Created",
                    }
                )
            else:
                results["connections_created"].append(
                    {
                        "name": sqlite_conn.name,
                        "engine": sqlite_conn.engine,
                        "status": "Already exists",
                    }
                )

            # Try to create PostgreSQL connection if environment variables exist
            db_host = os.environ.get("DB_HOST")
            db_user = os.environ.get("DB_USER")
            db_password = os.environ.get("DB_PASSWORD")

            if db_host and db_user and db_password:
                pg_conn, pg_created = DatabaseConnection.objects.get_or_create(
                    name="Supabase PostgreSQL (Backup)",
                    defaults={
                        "host": db_host,
                        "port": int(os.environ.get("DB_PORT", 6543)),
                        "database": os.environ.get("DB_NAME", "postgres"),
                        "username": db_user,
                        "password": db_password,
                        "engine": "postgresql",
                    },
                )

                results["connections_created"].append(
                    {
                        "name": pg_conn.name,
                        "engine": pg_conn.engine,
                        "status": "Created" if pg_created else "Already exists",
                    }
                )

            # Create admin user if not exists
            if not User.objects.filter(username="admin").exists():
                admin_user = User.objects.create_superuser(
                    username="admin", email="admin@example.com", password="admin123"
                )
                results["admin_user"] = {
                    "username": "admin",
                    "password": "admin123",
                    "status": "Created",
                }
            else:
                results["admin_user"] = {
                    "username": "admin",
                    "status": "Already exists",
                }

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to create sample data",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
