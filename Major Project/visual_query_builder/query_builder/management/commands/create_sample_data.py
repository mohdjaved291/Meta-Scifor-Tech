from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from query_builder.models import DatabaseConnection, QueryHistory
import json


class Command(BaseCommand):
    help = "Create sample database connections and data for testing"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🚀 Creating sample data for Visual Query Builder...")
        )

        # Create sample database connections
        self.create_sample_connections()

        # Create sample admin user if not exists
        self.create_admin_user()

        # Create sample query history
        self.create_sample_queries()

        self.stdout.write(self.style.SUCCESS("✅ Sample data created successfully!"))
        self.stdout.write(self.style.WARNING("📋 Next steps:"))
        self.stdout.write("   1. Go to your app: https://your-app.onrender.com")
        self.stdout.write('   2. Select "Sample SQLite Database" from dropdown')
        self.stdout.write("   3. Start building queries with drag & drop!")

    def create_sample_connections(self):
        """Create sample database connections"""

        # SQLite sample connection
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

        if created:
            self.stdout.write(f"✅ Created SQLite connection: {sqlite_conn.name}")
        else:
            self.stdout.write(
                f"📝 SQLite connection already exists: {sqlite_conn.name}"
            )

        # PostgreSQL sample connection (if user has Supabase)
        import os

        db_host = os.environ.get("DB_HOST")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD")

        if db_host and db_user and db_password:
            pg_conn, created = DatabaseConnection.objects.get_or_create(
                name="Supabase PostgreSQL",
                defaults={
                    "host": db_host,
                    "port": int(os.environ.get("DB_PORT", 6543)),
                    "database": os.environ.get("DB_NAME", "postgres"),
                    "username": db_user,
                    "password": db_password,
                    "engine": "postgresql",
                },
            )

            if created:
                self.stdout.write(f"✅ Created PostgreSQL connection: {pg_conn.name}")
            else:
                self.stdout.write(
                    f"📝 PostgreSQL connection already exists: {pg_conn.name}"
                )

    def create_admin_user(self):
        """Create admin user if not exists"""

        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser(
                username="admin", email="admin@example.com", password="admin123"
            )
            self.stdout.write(f"✅ Created admin user: admin / admin123")
        else:
            self.stdout.write(f"📝 Admin user already exists")

    def create_sample_queries(self):
        """Create sample query history"""

        admin_user = User.objects.filter(username="admin").first()
        if not admin_user:
            return

        sqlite_conn = DatabaseConnection.objects.filter(
            name="Sample SQLite Database"
        ).first()
        if not sqlite_conn:
            return

        sample_queries = [
            {
                "query": "SELECT * FROM users LIMIT 10",
                "visual_query": {
                    "tables": ["users"],
                    "columns": ["*"],
                    "joins": [],
                    "where": [],
                    "groupBy": [],
                    "orderBy": [],
                },
                "execution_time": 0.05,
                "rows_returned": 10,
                "optimization_suggestions": ["Query looks good!"],
            },
            {
                "query": "SELECT name, email FROM users WHERE age > 25 ORDER BY name",
                "visual_query": {
                    "tables": ["users"],
                    "columns": ["users.name", "users.email"],
                    "joins": [],
                    "where": [{"column": "users.age", "operator": ">", "value": "25"}],
                    "groupBy": [],
                    "orderBy": [{"column": "users.name", "direction": "ASC"}],
                },
                "execution_time": 0.12,
                "rows_returned": 8,
                "optimization_suggestions": ["Consider adding index on age column"],
            },
            {
                "query": "SELECT COUNT(*) as total_orders, status FROM orders GROUP BY status",
                "visual_query": {
                    "tables": ["orders"],
                    "columns": ["COUNT(*) as total_orders", "orders.status"],
                    "joins": [],
                    "where": [],
                    "groupBy": ["orders.status"],
                    "orderBy": [],
                },
                "execution_time": 0.08,
                "rows_returned": 3,
                "optimization_suggestions": ["Aggregation query is optimized"],
            },
        ]

        for query_data in sample_queries:
            query_obj, created = QueryHistory.objects.get_or_create(
                user=admin_user,
                database=sqlite_conn,
                query=query_data["query"],
                defaults={
                    "visual_query": query_data["visual_query"],
                    "execution_time": query_data["execution_time"],
                    "rows_returned": query_data["rows_returned"],
                    "optimization_suggestions": query_data["optimization_suggestions"],
                },
            )

            if created:
                self.stdout.write(
                    f'✅ Created sample query: {query_data["query"][:50]}...'
                )
            else:
                self.stdout.write(
                    f'📝 Sample query already exists: {query_data["query"][:50]}...'
                )
