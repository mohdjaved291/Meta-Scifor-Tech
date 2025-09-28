from __future__ import annotations
import sqlite3
import time
from typing import Dict, List, Any, Tuple

try:
    import psycopg2
    import psycopg2.extras

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
        try:
            if self.config["engine"] == "sqlite":
                self.connection = sqlite3.connect(self.config["database"])

            elif self.config["engine"] == "postgresql":
                if not HAS_POSTGRESQL:
                    raise ImportError(
                        "PostgreSQL support not available. Install psycopg2-binary."
                    )

                # Enhanced connection parameters for encoding fixes
                conn_params = {
                    "host": self.config["host"],
                    "port": self.config["port"],
                    "database": self.config["database"],
                    "user": self.config["username"],
                    "password": self.config["password"],
                    "sslmode": "require",
                    "connect_timeout": 30,
                    "application_name": "VisualQueryBuilder",
                    # ENCODING FIXES
                    "client_encoding": "UTF8",
                    "options": "-c timezone=UTC -c client_encoding=UTF8",
                }

                print(f"🔗 Connecting to PostgreSQL with encoding fixes...")
                self.connection = psycopg2.connect(**conn_params)

                # Explicitly set encoding after connection
                with self.connection.cursor() as cursor:
                    cursor.execute("SET client_encoding = 'UTF8'")
                    cursor.execute("SET timezone = 'UTC'")
                    cursor.execute(
                        "SET default_transaction_isolation = 'read committed'"
                    )
                self.connection.commit()

                print(f"✅ PostgreSQL connected with UTF8 encoding")

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
                    charset="utf8mb4",
                )

            elif self.config["engine"] == "oracle":
                raise NotImplementedError("Oracle support not yet implemented.")

            return True

        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def get_schema(self) -> Dict[str, List[Dict]]:
        """Get database schema information with proper encoding"""
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
                            "record_count": 1000,  # Default for SQLite
                            "has_indexes": False,
                        },
                    }

            elif self.config["engine"] == "postgresql":
                # Set encoding for this session
                cursor.execute("SET client_encoding = 'UTF8'")

                # Get all tables
                cursor.execute(
                    """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
                )
                tables = [row[0] for row in cursor.fetchall()]

                print(f"📊 Found {len(tables)} tables in database")

                for table in tables:
                    # Get column information with primary key detection
                    cursor.execute(
                        """
                        SELECT 
                            c.column_name,
                            c.data_type,
                            c.is_nullable,
                            c.column_default,
                            CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key
                        FROM information_schema.columns c
                        LEFT JOIN (
                            SELECT ku.column_name
                            FROM information_schema.key_column_usage ku
                            JOIN information_schema.table_constraints tc 
                                ON ku.constraint_name = tc.constraint_name
                            WHERE tc.constraint_type = 'PRIMARY KEY' 
                                AND ku.table_name = %s
                        ) pk ON c.column_name = pk.column_name
                        WHERE c.table_name = %s
                        ORDER BY c.ordinal_position
                    """,
                        (table, table),
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

                    # Get row count safely
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        row_count = cursor.fetchone()[0]
                    except:
                        row_count = 0

                    schema[table] = {
                        "columns": columns,
                        "stats": {
                            "record_count": row_count,
                            "has_indexes": True,
                        },
                    }

                print(f"✅ Schema extracted successfully for {len(schema)} tables")

        except Exception as e:
            print(f"❌ Schema extraction error: {e}")
            import traceback

            traceback.print_exc()

        return schema

    def execute_query(self, sql: str) -> Tuple[List[Dict], float]:
        """Execute a SQL query and return results with execution time"""
        if not self.connection:
            return [], 0.0

        cursor = self.connection.cursor()
        start_time = time.time()

        try:
            # Set encoding for PostgreSQL queries
            if self.config["engine"] == "postgresql":
                cursor.execute("SET client_encoding = 'UTF8'")

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
            print(f"❌ Query execution error: {e}")
            return [{"error": str(e)}], time.time() - start_time

    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
                print("✅ Database connection closed successfully")
            except Exception as e:
                print(f"❌ Error closing connection: {e}")
            finally:
                self.connection = None
