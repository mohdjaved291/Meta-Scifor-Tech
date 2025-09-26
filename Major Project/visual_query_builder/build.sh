#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data
mkdir -p staticfiles
mkdir -p templates

# Check if frontend directory exists and build React app
if [ -d "frontend" ]; then
    echo "Building React frontend..."
    cd frontend
    
    # Install Node dependencies
    npm install
    
    # Build the React app
    npm run build
    
    # Copy build files to templates and static directories
    echo "Copying React build files..."
    if [ -d "build" ]; then
        # Copy index.html to templates
        cp build/index.html ../templates/
        
        # Copy static files
        if [ -d "build/static" ]; then
            cp -r build/static/* ../staticfiles/
        fi
        
        # Copy any other assets
        if [ -d "build/manifest.json" ]; then
            cp build/manifest.json ../staticfiles/
        fi
    fi
    
    cd ..
else
    echo "No frontend directory found, skipping React build..."
    # Create a basic index.html template if frontend doesn't exist
    echo '<!DOCTYPE html>
<html>
<head>
    <title>Visual Query Builder</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div id="root">
        <h1>Visual Database Query Builder</h1>
        <p>Backend API is running. Frontend not configured.</p>
        <p>Visit <a href="/api/">/api/</a> for API endpoints.</p>
    </div>
</body>
</html>' > templates/index.html
fi

# Add system check
echo "Running Django system checks..."
python manage.py check --settings=visual_query_builder.render_settings

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=visual_query_builder.render_settings

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --settings=visual_query_builder.render_settings

# Create superuser if it doesn't exist
echo "Creating admin superuser..."
python manage.py shell --settings=visual_query_builder.render_settings << 'EOF'
from django.contrib.auth.models import User
import os

username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
password = os.environ.get('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superuser created successfully!")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
else:
    print(f"ℹ️ Superuser '{username}' already exists")
    print(f"Use existing credentials to login to /admin/")
EOF

echo "Build completed successfully!"