#!/usr/bin/env bash
# build.sh - Render build script for Visual API Designer
# Place this file at the same level as manage.py

set -o errexit  # Exit on error

echo "🚀 Building Visual API Designer Backend..."

# Print Python version for debugging
echo "🐍 Python version: $(python --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
echo "📁 Creating static files directory..."
mkdir -p staticfiles

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create cache table (if using database cache)
echo "💾 Setting up cache table..."
python manage.py createcachetable 2>/dev/null || echo "Cache table creation skipped"

# Check for any system issues
echo "🔍 Running system check..."
python manage.py check --deploy

# Optional: Create superuser from environment variables
echo "👤 Setting up superuser..."
if [[ $CREATE_SUPERUSER == "True" ]]; then
    echo "Creating superuser from environment variables..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('SUPERUSER_USERNAME', 'admin')
email = os.environ.get('SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
EOF
else
    echo "Superuser creation skipped (set CREATE_SUPERUSER=True to enable)"
fi

# Verify installation
echo "✅ Verifying installation..."
python -c "
import django
import rest_framework
print(f'Django version: {django.get_version()}')
print('✅ All imports successful')
"

echo "🎉 Build completed successfully!"
echo "🚀 Ready to deploy Visual API Designer Backend"