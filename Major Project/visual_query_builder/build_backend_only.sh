#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting backend-only build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data
mkdir -p staticfiles
mkdir -p templates

# Create a simple index.html for the backend
echo "Creating simple frontend template..."
cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Database Query Builder - API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .api-endpoint {
            background: #f8f9fa;
            padding: 10px;
            border-left: 4px solid #007bff;
            margin: 10px 0;
            font-family: monospace;
        }
        .status {
            color: #28a745;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Visual Database Query Builder</h1>
        <p class="status">✅ Backend API is running successfully!</p>
        
        <h2>Available API Endpoints:</h2>
        
        <div class="api-endpoint">
            <strong>GET</strong> /api/connections/ - List database connections
        </div>
        
        <div class="api-endpoint">
            <strong>POST</strong> /api/connections/ - Create database connection
        </div>
        
        <div class="api-endpoint">
            <strong>GET</strong> /api/connections/{id}/schema/ - Get database schema
        </div>
        
        <div class="api-endpoint">
            <strong>POST</strong> /api/query/build/ - Build SQL query from visual components
        </div>
        
        <div class="api-endpoint">
            <strong>POST</strong> /api/query/execute/ - Execute SQL query
        </div>
        
        <div class="api-endpoint">
            <strong>GET</strong> /api/query/history/ - Get query history
        </div>
        
        <div class="api-endpoint">
            <strong>GET</strong> /api/analytics/ - Get performance analytics
        </div>
        
        <h2>Admin Interface:</h2>
        <p><a href="/admin/" target="_blank">Django Admin Panel</a> - Manage database connections and view query history</p>
        
        <h2>Next Steps:</h2>
        <ul>
            <li>Use the API endpoints to build your frontend application</li>
            <li>Test endpoints using tools like Postman or curl</li>
            <li>Create database connections via the admin panel</li>
            <li>Deploy the React frontend as a separate service or integrate it later</li>
        </ul>
        
        <h2>Documentation:</h2>
        <p>This Django REST API provides endpoints for building and executing database queries visually. The backend includes:</p>
        <ul>
            <li><strong>Query Analysis:</strong> Analyze SQL complexity and performance</li>
            <li><strong>Performance Prediction:</strong> AI-powered execution time estimation</li>
            <li><strong>Multi-Database Support:</strong> PostgreSQL, MySQL, SQLite</li>
            <li><strong>Query History:</strong> Track and analyze past queries</li>
            <li><strong>Visual to SQL Conversion:</strong> Convert drag-and-drop components to SQL</li>
        </ul>
    </div>
</body>
</html>
EOF

# Copy any existing static files
if [ -d "static" ]; then
    echo "Copying existing static files..."
    cp -r static/* staticfiles/ 2>/dev/null || true
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=visual_query_builder.render_settings

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --settings=visual_query_builder.render_settings

# Create superuser if needed (optional)
echo "Creating default admin user..."
python manage.py shell --settings=visual_query_builder.render_settings << 'EOF'
from django.contrib.auth.models import User
import os

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password=os.environ.get('ADMIN_PASSWORD', 'admin123')
    )
    print("Default admin user created: admin/admin123")
else:
    print("Admin user already exists")
EOF

echo "Backend build completed successfully!"
echo "API will be available at: https://your-app-name.onrender.com/api/"
echo "Admin panel at: https://your-app-name.onrender.com/admin/"