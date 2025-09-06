#!/bin/bash

# Setup script for Django Property Listings with Redis Caching
# This script automates the initial setup process

echo "🏗️  Setting up Django Property Listings with Redis Caching..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Populate sample data
echo "📝 Populating sample data..."
python manage.py populate_properties

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the development server:"
echo "   python manage.py runserver"
echo ""
echo "🌐 Available endpoints:"
echo "   http://localhost:8000/properties/          - JSON API"
echo "   http://localhost:8000/properties/html/     - HTML interface"
echo "   http://localhost:8000/properties/cache/metrics/ - Cache metrics"
echo "   http://localhost:8000/admin/               - Admin interface"
echo ""
echo "🧪 To run tests:"
echo "   python manage.py test"