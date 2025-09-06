@echo off
REM Setup script for Django Property Listings with Redis Caching (Windows)

echo 🏗️  Setting up Django Property Listings with Redis Caching...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Start Docker services
echo 🐳 Starting Docker services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Run migrations
echo 🗄️  Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Populate sample data
echo 📝 Populating sample data...
python manage.py populate_properties

echo ✅ Setup complete!
echo.
echo 🚀 To start the development server:
echo    python manage.py runserver
echo.
echo 🌐 Available endpoints:
echo    http://localhost:8000/properties/          - JSON API
echo    http://localhost:8000/properties/html/     - HTML interface
echo    http://localhost:8000/properties/cache/metrics/ - Cache metrics
echo    http://localhost:8000/admin/               - Admin interface
echo.
echo 🧪 To run tests:
echo    python manage.py test

pause
