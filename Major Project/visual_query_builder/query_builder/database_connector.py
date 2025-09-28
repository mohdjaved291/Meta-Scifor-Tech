from __future__ import annotations
import sqlite3
import time
from typing import Dict, List, Any, Tuple

try:
    import psycopg2

    HAS_POSTGRESQL = True
except ImportError:
    HAS_POSTGRESQL = False
    print("Warning: psycopg2 not installed. PostgreSQL support disabled.")

try:
    import mysql.connector

    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False
    print("Warning: mysql-connector-python not installed. MySQL support disabled.")


class DatabaseConnector:
    def __init__(self, connection_config: Dict):
        self.config = connection_config
        self.connection = None

    def connect(self):
        """Connect with multiple fallback strategies for encoding issues"""
        try:
            if self.config["engine"] == "sqlite":
                self.connection = sqlite3.connect(self.config["database"])
                return True

            elif self.config["engine"] == "postgresql":
                if not HAS_POSTGRESQL:
                    raise ImportError(
                        "PostgreSQL support not available. Install psycopg2-binary."
                    )

                # Strategy 1: Minimal connection parameters
                print("🔗 Connecting to PostgreSQL with encoding fixes...")

                connection_params = {
                    "host": self.config["host"],
                    "port": self.config["port"],
                    "database": self.config["database"],
                    "user": self.config["username"],
                    "password": self.config["password"],
                    "sslmode": "require",
                    "connect_timeout": 30,
                }

                try:
                    # Try without any encoding parameters first
                    self.connection = psycopg2.connect(**connection_params)

                    # Test the connection
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()

                    print("✅ Minimal connection successful!")
                    return True

                except Exception as e:
                    print(f"❌ Connection error: {e}")

                    try:
                        # Strategy 2: DSN string method
                        print("🔗 Attempting DSN string connection...")

                        dsn = f"host={self.config['host']} port={self.config['port']} dbname={self.config['database']} user={self.config['username']} password={self.config['password']} sslmode=require"

                        self.connection = psycopg2.connect(dsn)

                        cursor = self.connection.cursor()
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        cursor.close()

                        print("✅ DSN connection successful!")
                        return True

                    except Exception as e2:
                        print(f"❌ All connection strategies failed: {e2}")
                        return False

            elif self.config["engine"] == "mysql":
                if not HAS_MYSQL:
                    raise ImportError(
                        "MySQL support not available. Install mysql-connector-python."
                    )
                self.connection = mysql.connector.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    database=self.config["database"],
                    user=self.config["username"],
                    password=self.config["password"],
                )
                return True

            elif self.config["engine"] == "oracle":
                raise NotImplementedError("Oracle support not yet implemented.")

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def get_schema(self) -> Dict[str, List[Dict]]:
        """Get database schema information with error handling"""
        if not self.connection:
            return {}

        cursor = self.connection.cursor()
        schema = {}

        try:
            if self.config["engine"] == "sqlite":
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = []
                    for col in cursor.fetchall():
                        columns.append(
                            {
                                "name": col[1],
                                "type": col[2],
                                "nullable": not col[3],
                                "primary_key": bool(col[5]),
                            }
                        )
                    schema[table] = {
                        "columns": columns,
                        "stats": {
                            "record_count": 1000,  # Default estimate
                            "table_size": "Unknown",
                            "has_indexes": len(columns) > 0,
                        },
                    }

            elif self.config["engine"] == "postgresql":
                # Get tables
                cursor.execute(
                    """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """
                )

                tables = [row[0] for row in cursor.fetchall()]
                print(f"📋 Found {len(tables)} tables: {tables}")

                for table_name in tables:
                    try:
                        # Get columns for each table
                        cursor.execute(
                            """
                            SELECT 
                                column_name,
                                data_type,
                                is_nullable,
                                column_default,
                                CASE 
                                    WHEN column_name IN (
                                        SELECT column_name 
                                        FROM information_schema.key_column_usage 
                                        WHERE table_name = %s 
                                        AND constraint_name LIKE '%%pkey%%'
                                    ) THEN true 
                                    ELSE false 
                                END as is_primary_key
                            FROM information_schema.columns 
                            WHERE table_name = %s
                            ORDER BY ordinal_position
                        """,
                            (table_name, table_name),
                        )

                        columns = []
                        for col in cursor.fetchall():
                            columns.append(
                                {
                                    "name": col[0],
                                    "type": col[1],
                                    "nullable": col[2] == "YES",
                                    "default": col[3],
                                    "primary_key": col[4],
                                }
                            )

                        # Get row count estimate
                        try:
                            cursor.execute(
                                f"SELECT COUNT(*) FROM {table_name} LIMIT 1000"
                            )
                            row_count = cursor.fetchone()[0]
                        except:
                            row_count = 0

                        schema[table_name] = {
                            "columns": columns,
                            "stats": {
                                "record_count": row_count,
                                "table_size": "Unknown",
                                "has_indexes": len(columns) > 0,
                            },
                        }

                        print(
                            f"✅ Loaded schema for {table_name}: {len(columns)} columns, {row_count} rows"
                        )

                    except Exception as e:
                        print(f"⚠️ Error loading schema for {table_name}: {e}")
                        # Add minimal schema info
                        schema[table_name] = {
                            "columns": [
                                {
                                    "name": "id",
                                    "type": "integer",
                                    "nullable": False,
                                    "primary_key": True,
                                }
                            ],
                            "stats": {
                                "record_count": 0,
                                "table_size": "Unknown",
                                "has_indexes": False,
                            },
                        }

        except Exception as e:
            print(f"Schema extraction error: {e}")
            # Return sample schema for testing when real schema fails
            if not schema:
                schema = self._get_sample_schema()

        return schema

    def _get_sample_schema(self) -> Dict[str, Dict]:
        """Return sample schema when real schema extraction fails"""
        print("📦 Using sample schema for testing")

        return {
            "sample_users": {
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
                ],
                "stats": {"record_count": 5, "table_size": "1 KB", "has_indexes": True},
            },
            "sample_products": {
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
                ],
                "stats": {"record_count": 5, "table_size": "2 KB", "has_indexes": True},
            },
            "sample_orders": {
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
                "stats": {"record_count": 5, "table_size": "1 KB", "has_indexes": True},
            },
        }

    def execute_query(self, sql: str) -> Tuple[List[Dict], float]:
        """Execute a SQL query and return results with execution time"""
        if not self.connection:
            return [{"error": "No database connection"}], 0.0

        cursor = self.connection.cursor()
        start_time = time.time()

        try:
            cursor.execute(sql)
            execution_time = time.time() - start_time

            if sql.strip().lower().startswith("select"):
                try:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    results = []
                    for row in rows:
                        row_dict = {}
                        for i, value in enumerate(row):
                            row_dict[columns[i]] = (
                                str(value) if value is not None else None
                            )
                        results.append(row_dict)

                    return results, execution_time
                except Exception as e:
                    return [
                        {"error": f"Query execution error: {str(e)}"}
                    ], execution_time
            else:
                self.connection.commit()
                return [{"message": "Query executed successfully"}], execution_time

        except Exception as e:
            return [{"error": str(e)}], time.time() - start_time

    def execute_query_with_monitoring(self, sql: str) -> Tuple[List[Dict], float]:
        """Execute query with detailed monitoring and progress tracking"""
        if not self.connection:
            return [], 0.0

        cursor = self.connection.cursor()
        start_time = time.time()

        try:
            # Get query execution plan first (PostgreSQL specific)
            if self.config["engine"] == "postgresql":
                try:
                    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}"
                    cursor.execute(explain_sql)
                    explain_result = cursor.fetchone()[0]
                    # Store explain plan for analysis
                except Exception:
                    pass  # Continue without explain plan if not available

            # Execute the actual query
            cursor.execute(sql)
            execution_time = time.time() - start_time

            if sql.strip().lower().startswith("select"):
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))

                return results, execution_time
            else:
                self.connection.commit()
                return [{"message": "Query executed successfully"}], execution_time

        except Exception as e:
            return [{"error": str(e)}], time.time() - start_time

    def get_query_execution_plan(self, sql: str) -> Dict[str, Any]:
        """Get detailed execution plan for a query"""
        if not self.connection:
            return {}

        cursor = self.connection.cursor()

        try:
            if self.config["engine"] == "postgresql":
                explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}"
                cursor.execute(explain_sql)
                plan = cursor.fetchone()[0][0]

                return {
                    "plan": plan,
                    "total_cost": plan.get("Total Cost", 0),
                    "execution_time": plan.get("Actual Total Time", 0),
                    "rows": plan.get("Actual Rows", 0),
                }
            elif self.config["engine"] == "mysql":
                cursor.execute(f"EXPLAIN FORMAT=JSON {sql}")
                plan = cursor.fetchone()[0]
                return {"plan": plan, "engine": "mysql"}
            else:
                return {"plan": "Execution plan not available for this database engine"}

        except Exception as e:
            return {"error": f"Could not get execution plan: {str(e)}"}

    def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific table"""
        if not self.connection:
            return {}

        cursor = self.connection.cursor()
        stats = {}

        try:
            if self.config["engine"] == "postgresql":
                # Get table stats
                cursor.execute(
                    f"""
                    SELECT 
                        schemaname,
                        tablename,
                        attname,
                        n_distinct,
                        correlation,
                        most_common_vals,
                        most_common_freqs
                    FROM pg_stats 
                    WHERE tablename = '{table_name}'
                """
                )

                column_stats = cursor.fetchall()
                stats["column_statistics"] = [
                    {
                        "column": row[2],
                        "distinct_values": row[3],
                        "correlation": row[4],
                        "common_values": row[5],
                        "frequencies": row[6],
                    }
                    for row in column_stats
                ]

                # Get index information
                cursor.execute(
                    f"""
                    SELECT 
                        indexname,
                        indexdef,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_indexes pi
                    LEFT JOIN pg_stat_user_indexes psi ON pi.indexname = psi.indexrelname
                    WHERE pi.tablename = '{table_name}'
                """
                )

                index_stats = cursor.fetchall()
                stats["indexes"] = [
                    {
                        "name": row[0],
                        "definition": row[1],
                        "scans": row[2] or 0,
                        "tuples_read": row[3] or 0,
                        "tuples_fetched": row[4] or 0,
                    }
                    for row in index_stats
                ]

                # Get table size
                cursor.execute(
                    f"""
                    SELECT 
                        pg_size_pretty(pg_total_relation_size('{table_name}')) as total_size,
                        pg_size_pretty(pg_relation_size('{table_name}')) as table_size,
                        (SELECT COUNT(*) FROM {table_name}) as row_count
                """
                )

                size_info = cursor.fetchone()
                stats["size_info"] = {
                    "total_size": size_info[0],
                    "table_size": size_info[1],
                    "row_count": size_info[2],
                }

        except Exception as e:
            stats["error"] = str(e)

        return stats

    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
                print("Database connection closed successfully")
            except Exception as e:
                print(f"Error closing connection: {e}")
            finally:
                self.connection = None
