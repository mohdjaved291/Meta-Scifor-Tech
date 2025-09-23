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
        try:
            if self.config["engine"] == "sqlite":
                self.connection = sqlite3.connect(self.config["database"])
            elif self.config["engine"] == "postgresql":
                if not HAS_POSTGRESQL:
                    raise ImportError(
                        "PostgreSQL support not available. Install psycopg2-binary."
                    )
                self.connection = psycopg2.connect(
                    host=self.config["host"],
                    port=self.config["port"],
                    database=self.config["database"],
                    user=self.config["username"],
                    password=self.config["password"],
                )
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
            elif self.config["engine"] == "oracle":
                raise NotImplementedError("Oracle support not yet implemented.")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def get_schema(self) -> Dict[str, List[Dict]]:
        """Get database schema information"""
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
                    schema[table] = columns

            elif self.config["engine"] == "postgresql":
                cursor.execute(
                    """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                )
                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    cursor.execute(
                        """
                        SELECT column_name, data_type, is_nullable, 
                               column_default, is_identity
                        FROM information_schema.columns 
                        WHERE table_name = %s
                    """,
                        (table,),
                    )

                    columns = []
                    for col in cursor.fetchall():
                        columns.append(
                            {
                                "name": col[0],
                                "type": col[1],
                                "nullable": col[2] == "YES",
                                "default": col[3],
                                "primary_key": col[4] == "YES",
                            }
                        )
                    schema[table] = columns

        except Exception as e:
            print(f"Schema extraction error: {e}")

        return schema

    def execute_query(self, sql: str) -> Tuple[List[Dict], float]:
        """Execute a SQL query and return results with execution time"""
        if not self.connection:
            return [], 0.0

        cursor = self.connection.cursor()
        start_time = time.time()

        try:
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
