#!/usr/bin/env python3
"""
Quick Start Script for Movie Recap Service
Handles complete setup and launch
"""

import os
import sys
import subprocess
import time
import platform
import webbrowser
from pathlib import Path


def log(message, level="INFO"):
    """Log formatted message."""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    
    prefix = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    
    color = colors.get(level, colors["INFO"])
    reset = colors["RESET"]
    icon = prefix.get(level, "ℹ️")
    
    print(f"{color}{icon} {message}{reset}")


def run_command(command, description, check=True):
    """Run command with logging."""
    log(f"Running: {description}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            log(f"✓ {description}", "SUCCESS")
            return True
        else:
            if check:
                log(f"✗ {description}: {result.stderr}", "ERROR")
                return False
            else:
                log(f"⚠ {description}: {result.stderr}", "WARNING")
                return True
    except Exception as e:
        log(f"Exception in {description}: {e}", "ERROR")
        return False


def check_prerequisites():
    """Check if required tools are installed."""
    log("Checking prerequisites...")
    
    tools = [
        ("python", "python --version", "Python 3.11+"),
        ("pip", "pip --version", "Python package manager"),
        ("docker", "docker --version", "Docker Engine"),
        ("docker-compose", "docker-compose --version", "Docker Compose"),
    ]
    
    missing = []
    for tool, command, description in tools:
        if not run_command(command, f"Check {tool}", check=False):
            missing.append((tool, description))
    
    if missing:
        log("Missing prerequisites:", "ERROR")
        for tool, desc in missing:
            log(f"  - {tool}: {desc}", "ERROR")
        
        log("\nInstallation instructions:", "INFO")
        if platform.system().lower() == "windows":
            log("Run: python install.py", "INFO")
        else:
            log("Run: sudo python3 install.py", "INFO")
        
        return False
    
    log("All prerequisites satisfied!", "SUCCESS")
    return True


def setup_environment():
    """Set up environment configuration."""
    log("Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        log("Created .env from template", "SUCCESS")
        
        # Basic environment setup
        with open(env_file, 'a') as f:
            f.write("\n# Quick start configuration\n")
            f.write("ENVIRONMENT=development\n")
            f.write("DEBUG=true\n")
            f.write("LOG_LEVEL=INFO\n")
        
        log("⚠️  Please edit .env file for production use", "WARNING")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    log("Installing Python dependencies...")
    
    commands = [
        ("python -m pip install --upgrade pip", "Upgrade pip"),
        ("pip install -r backend/requirements.txt", "Install backend dependencies"),
        ("pip install -r requirements-test.txt", "Install test dependencies"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            log("Trying alternative installation...", "WARNING")
            # Install core dependencies only
            core_deps = [
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0",
                "sqlalchemy>=2.0.0",
                "redis>=5.0.0",
                "python-dotenv>=1.0.0"
            ]
            
            for dep in core_deps:
                run_command(f"pip install {dep}", f"Install {dep}", check=False)
            break
    
    return True


def start_services():
    """Start all services using Docker Compose."""
    log("Starting services with Docker Compose...")
    
    # Stop any existing containers
    run_command("docker-compose down", "Stop existing containers", check=False)
    
    # Start services
    success = run_command(
        "docker-compose up -d postgres redis",
        "Start database and cache services"
    )
    
    if success:
        log("Waiting for services to be ready...", "INFO")
        time.sleep(10)
        
        # Check if services are healthy
        if run_command("docker-compose ps", "Check service status", check=False):
            log("Core services started successfully", "SUCCESS")
            return True
    
    # Fallback: try to start services manually
    log("Trying to start services manually...", "WARNING")
    
    # Try to start PostgreSQL locally
    system = platform.system().lower()
    if system == "windows":
        run_command("net start postgresql-x64-14", "Start PostgreSQL", check=False)
        run_command("redis-server --service-start", "Start Redis", check=False)
    elif system == "linux":
        run_command("sudo service postgresql start", "Start PostgreSQL", check=False)
        run_command("sudo service redis-server start", "Start Redis", check=False)
    elif system == "darwin":  # macOS
        run_command("brew services start postgresql", "Start PostgreSQL", check=False)
        run_command("brew services start redis", "Start Redis", check=False)
    
    return True


def setup_database():
    """Set up database schema."""
    log("Setting up database...")
    
    # Wait a bit more for database to be ready
    time.sleep(5)
    
    # Try to create database
    create_db_commands = [
        ("createdb movie_recap", "Create main database"),
        ("createdb test_movie_recap", "Create test database"),
    ]
    
    for command, description in create_db_commands:
        run_command(command, description, check=False)
    
    # Run migrations if Alembic is available
    if Path("backend/alembic").exists():
        os.chdir("backend")
        success = run_command("alembic upgrade head", "Run database migrations")
        os.chdir("..")
        
        if not success:
            log("Database migrations failed - will run on first start", "WARNING")
    
    return True


def start_application():
    """Start the FastAPI application."""
    log("Starting Movie Recap Service...")
    
    os.chdir("backend")
    
    # Start the application
    log("🚀 Starting FastAPI server on http://localhost:8000", "INFO")
    log("📚 API documentation will be available at http://localhost:8000/docs", "INFO")
    
    try:
        # Start in development mode
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload",
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        log("Application stopped by user", "INFO")
    except Exception as e:
        log(f"Failed to start application: {e}", "ERROR")
        return False
    
    return True


def open_browser():
    """Open browser to application URLs."""
    urls = [
        ("http://localhost:8000/docs", "API Documentation"),
        ("http://localhost:8000", "Application"),
        ("http://localhost:5555", "Celery Flower (if running)"),
        ("http://localhost:3000", "Grafana Monitoring (if running)"),
    ]
    
    log("Opening browser...", "INFO")
    
    for url, description in urls:
        try:
            webbrowser.open(url)
            log(f"Opened {description}: {url}", "SUCCESS")
            break  # Open only the first successful one
        except:
            continue


def main():
    """Main quick start function."""
    print("🎬 Movie Recap Service - Quick Start")
    print("=" * 50)
    
    steps = [
        (check_prerequisites, "Check Prerequisites"),
        (setup_environment, "Setup Environment"),
        (install_dependencies, "Install Dependencies"), 
        (start_services, "Start Services"),
        (setup_database, "Setup Database"),
    ]
    
    # Run setup steps
    for step_func, step_name in steps:
        try:
            log(f"\n--- {step_name} ---", "INFO")
            if not step_func():
                log(f"Failed at step: {step_name}", "ERROR")
                log("Please check the logs and try again", "ERROR")
                return 1
        except Exception as e:
            log(f"Exception in {step_name}: {e}", "ERROR")
            return 1
    
    log("\n🎉 Setup completed successfully!", "SUCCESS")
    log("Starting the application...", "INFO")
    
    # Open browser after a short delay
    import threading
    def delayed_browser_open():
        time.sleep(3)
        open_browser()
    
    threading.Thread(target=delayed_browser_open, daemon=True).start()
    
    # Start application (this will block)
    try:
        start_application()
    except KeyboardInterrupt:
        log("\n👋 Goodbye!", "INFO")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())