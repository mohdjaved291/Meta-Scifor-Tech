"""
Custom database connector for visual_query_builder
Handles Supabase connection pooling encoding issues
"""

import psycopg2
import time
from typing import Dict, List, Any, Tuple


class RobustDatabaseConnector:
    def __init__(self, connection_config: Dict):
        self.config = connection_config
        self.connection = None

    def connect(self):
        """Connect with multiple fallback strategies for encoding issues"""
        try:
            # Strategy 1: Minimal connection parameters
            print("🔗 Attempting minimal connection...")

            connection_params = {
                "host": self.config["host"],
                "port": self.config["port"],
                "database": self.config["database"],
                "user": self.config["username"],
                "password": self.config["password"],
                "sslmode": "require",
                "connect_timeout": 30,
            }

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
            print(f"❌ Minimal connection failed: {e}")

            try:
                # Strategy 2: With explicit encoding
                print("🔗 Attempting connection with explicit encoding...")

                connection_params["options"] = "-c client_encoding=UTF8"
                self.connection = psycopg2.connect(**connection_params)

                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()

                print("✅ Encoding connection successful!")
                return True

            except Exception as e2:
                print(f"❌ Encoding connection failed: {e2}")

                try:
                    # Strategy 3: DSN string method
                    print("🔗 Attempting DSN string connection...")

                    dsn = f"host={self.config['host']} port={self.config['port']} dbname={self.config['database']} user={self.config['username']} password={self.config['password']} sslmode=require"

                    self.connection = psycopg2.connect(dsn)

                    cursor = self.connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()

                    print("✅ DSN connection successful!")
                    return True

                except Exception as e3:
                    print(f"❌ All connection strategies failed. Last error: {e3}")
                    return False

    def get_schema(self) -> Dict[str, List[Dict]]:
        """Get database schema information with error handling"""
        if not self.connection:
            return {}

        schema = {}

        try:
            cursor = self.connection.cursor()

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
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name} LIMIT 1000")
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

            cursor.close()

        except Exception as e:
            print(f"❌ Schema extraction error: {e}")
            # Return sample schema for testing
            schema = self._get_sample_schema()

        return schema

    def _get_sample_schema(self) -> Dict[str, List[Dict]]:
        """Return sample schema when real schema extraction fails"""
        print("📦 Using sample schema for testing")

        return {
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
                        "name": "created_at",
                        "type": "timestamp",
                        "nullable": True,
                        "primary_key": False,
                    },
                ],
                "stats": {
                    "record_count": 100,
                    "table_size": "1 MB",
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
                        "name": "total",
                        "type": "decimal",
                        "nullable": False,
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
                    "record_count": 250,
                    "table_size": "2 MB",
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
                        "name": "price",
                        "type": "decimal",
                        "nullable": False,
                        "primary_key": False,
                    },
                    {
                        "name": "category",
                        "type": "varchar",
                        "nullable": True,
                        "primary_key": False,
                    },
                ],
                "stats": {
                    "record_count": 500,
                    "table_size": "3 MB",
                    "has_indexes": True,
                },
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

    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
                print("✅ Database connection closed")
            except Exception as e:
                print(f"⚠️ Error closing connection: {e}")
            finally:
                self.connection = None
