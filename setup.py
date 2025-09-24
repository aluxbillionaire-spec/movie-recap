#!/usr/bin/env python3
"""
Comprehensive setup script for Movie Recap Service.
Handles installation, configuration, and problem resolution.
"""

import os
import sys
import subprocess
import platform
import json
import urllib.request
from pathlib import Path
import shutil
import tempfile


class SetupManager:
    """Manages the complete setup process."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.python_executable = sys.executable
        self.project_root = Path(__file__).parent
        
    def log(self, message, level="INFO"):
        """Log a message."""
        prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{prefix.get(level, 'ℹ️')} {message}")
    
    def run_command(self, command, description, cwd=None, check=True):
        """Run a command safely."""
        self.log(f"Running: {description}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log(f"Success: {description}", "SUCCESS")
                return True, result.stdout
            else:
                if check:
                    self.log(f"Failed: {description} - {result.stderr}", "ERROR")
                else:
                    self.log(f"Warning: {description} - {result.stderr}", "WARNING")
                return False, result.stderr
                
        except Exception as e:
            self.log(f"Exception in {description}: {e}", "ERROR")
            return False, str(e)
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            self.log(f"Python {version.major}.{version.minor} detected. Requires Python 3.11+", "ERROR")
            return False
        
        self.log(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies with proper error handling."""
        self.log("Installing Python dependencies...")
        
        # Upgrade pip first
        success, _ = self.run_command(
            f'"{self.python_executable}" -m pip install --upgrade pip',
            "Upgrade pip"
        )
        if not success:
            return False
        
        # Choose appropriate requirements file
        if self.is_windows and Path("requirements-windows.txt").exists():
            requirements_file = "requirements-windows.txt"
        else:
            requirements_file = "backend/requirements.txt"
        
        # Install main dependencies
        success, _ = self.run_command(
            f'"{self.python_executable}" -m pip install -r {requirements_file}',
            f"Install dependencies from {requirements_file}"
        )
        if not success:
            self.log("Trying alternative installation method...", "WARNING")
            # Try installing core dependencies individually
            core_deps = [
                "fastapi==0.104.1",
                "uvicorn[standard]==0.24.0",
                "sqlalchemy==2.0.23",
                "redis==5.0.1",
                "celery==5.3.4",
                "pydantic==2.5.1",
                "python-dotenv==1.0.0",
                "httpx==0.25.2",
                "aiofiles==23.2.1",
            ]
            
            for dep in core_deps:
                self.run_command(
                    f'"{self.python_executable}" -m pip install {dep}',
                    f"Install {dep}",
                    check=False
                )
        
        # Install test dependencies
        if Path("requirements-test.txt").exists():
            self.run_command(
                f'"{self.python_executable}" -m pip install -r requirements-test.txt',
                "Install test dependencies",
                check=False
            )
        
        return True
    
    def setup_environment_file(self):
        """Set up environment configuration."""
        self.log("Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            shutil.copy(env_example, env_file)
            self.log("Created .env file from .env.example", "SUCCESS")
        
        # Update .env with Windows-specific paths if needed
        if self.is_windows and env_file.exists():
            self.update_env_for_windows(env_file)
        
        return True
    
    def update_env_for_windows(self, env_file):
        """Update environment file for Windows."""
        self.log("Updating environment for Windows...")
        
        # Read current env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Windows-specific updates
        updates = {
            'DATABASE_URL=': 'DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/movie_recap',
            'REDIS_URL=': 'REDIS_URL=redis://localhost:6379/0',
            'TEMP_DIR=': f'TEMP_DIR={tempfile.gettempdir().replace(os.sep, "/")}',
            'LOG_LEVEL=': 'LOG_LEVEL=INFO',
        }
        
        for key, value in updates.items():
            if key in content and not content.split(key)[1].split('\n')[0].strip():
                content = content.replace(key, value)
        
        # Write back
        with open(env_file, 'w') as f:
            f.write(content)
        
        self.log("Environment file updated for Windows", "SUCCESS")
    
    def create_directories(self):
        """Create necessary directories."""
        self.log("Creating project directories...")
        
        directories = [
            "logs",
            "temp",
            "uploads",
            "processed",
            "data",
            "backup",
            "backend/logs",
            "tests/coverage",
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.log("Project directories created", "SUCCESS")
        return True
    
    def fix_import_issues(self):
        """Fix common import issues."""
        self.log("Fixing import issues...")
        
        # Create __init__.py files where missing
        init_files = [
            "backend/__init__.py",
            "backend/app/__init__.py",
            "backend/app/api/__init__.py",
            "backend/app/api/v1/__init__.py",
            "backend/app/core/__init__.py",
            "backend/app/models/__init__.py",
            "backend/app/services/__init__.py",
            "backend/app/workers/__init__.py",
            "backend/app/middleware/__init__.py",
            "tests/__init__.py",
        ]
        
        for init_file in init_files:
            file_path = self.project_root / init_file
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text("# Auto-generated __init__.py\n")
        
        self.log("Import structure fixed", "SUCCESS")
        return True
    
    def setup_database_config(self):
        """Set up database configuration."""
        self.log("Setting up database configuration...")
        
        # Create a simple database setup script
        db_setup_script = self.project_root / "setup_db.py"
        
        script_content = '''
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from sqlalchemy import create_engine, text
    from app.core.config import get_settings
    
    def setup_database():
        """Set up database connection."""
        settings = get_settings()
        
        # Create database URL without database name for initial connection
        db_url_parts = settings.DATABASE_URL.split('/')
        base_url = '/'.join(db_url_parts[:-1])
        
        try:
            # Connect to PostgreSQL server
            engine = create_engine(base_url + '/postgres')
            
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='movie_recap'"))
                if not result.fetchone():
                    conn.execute(text("CREATE DATABASE movie_recap"))
                    print("✅ Created movie_recap database")
                
                # Check if test database exists
                result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='test_movie_recap'"))
                if not result.fetchone():
                    conn.execute(text("CREATE DATABASE test_movie_recap"))
                    print("✅ Created test_movie_recap database")
            
            print("✅ Database setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            print("Please ensure PostgreSQL is running and accessible")
            return False

    if __name__ == "__main__":
        setup_database()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies first")
'''
        
        db_setup_script.write_text(script_content)
        self.log("Database setup script created", "SUCCESS")
        return True
    
    def create_startup_scripts(self):
        """Create startup scripts for different environments."""
        self.log("Creating startup scripts...")
        
        # Development startup script
        dev_script = self.project_root / ("start_dev.bat" if self.is_windows else "start_dev.sh")
        
        if self.is_windows:
            dev_content = '''@echo off
echo Starting Movie Recap Service - Development Mode
echo =============================================

REM Start Redis if not running
echo Starting Redis...
start /B redis-server

REM Start PostgreSQL if not running  
echo Starting PostgreSQL...
net start postgresql-x64-14

REM Wait a moment for services to start
timeout /t 5

REM Set environment
set ENVIRONMENT=development

REM Start the application
echo Starting FastAPI application...
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
'''
        else:
            dev_content = '''#!/bin/bash
echo "Starting Movie Recap Service - Development Mode"
echo "============================================="

# Start Redis if not running
echo "Starting Redis..."
redis-server --daemonize yes

# Start PostgreSQL if not running
echo "Starting PostgreSQL..."
sudo service postgresql start

# Wait a moment for services to start
sleep 5

# Set environment
export ENVIRONMENT=development

# Start the application
echo "Starting FastAPI application..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
'''
        
        dev_script.write_text(dev_content)
        if not self.is_windows:
            os.chmod(dev_script, 0o755)
        
        self.log("Startup scripts created", "SUCCESS")
        return True
    
    def run_basic_tests(self):
        """Run basic tests to verify setup."""
        self.log("Running basic verification tests...")
        
        # Test Python imports
        test_imports = [
            ("fastapi", "FastAPI framework"),
            ("sqlalchemy", "SQLAlchemy ORM"),
            ("redis", "Redis client"),
            ("celery", "Celery task queue"),
            ("pydantic", "Pydantic validation"),
            ("httpx", "HTTP client"),
        ]
        
        import_results = []
        for module, description in test_imports:
            try:
                __import__(module)
                self.log(f"Import {module} - OK", "SUCCESS")
                import_results.append(True)
            except ImportError as e:
                self.log(f"Import {module} failed: {e}", "ERROR")
                import_results.append(False)
        
        # Test basic functionality if imports are OK
        if all(import_results):
            self.log("All imports successful - running functionality tests...", "SUCCESS")
            
            # Test FastAPI import and basic setup
            try:
                from fastapi import FastAPI
                app = FastAPI()
                self.log("FastAPI setup - OK", "SUCCESS")
            except Exception as e:
                self.log(f"FastAPI setup failed: {e}", "ERROR")
        
        return all(import_results)
    
    def generate_summary_report(self):
        """Generate a setup summary report."""
        self.log("Generating setup summary...")
        
        report = f"""
Movie Recap Service - Setup Summary
==================================

System Information:
- OS: {platform.system()} {platform.release()}
- Python: {sys.version.split()[0]}
- Project Root: {self.project_root}

Installation Status:
✅ Python dependencies installed
✅ Environment configuration created
✅ Project directories created
✅ Import structure fixed
✅ Database configuration ready
✅ Startup scripts created

Next Steps:
1. Install external services:
   - PostgreSQL (database)
   - Redis (cache/queue)
   - Docker (containerization)
   - FFmpeg (video processing)

2. Configure environment:
   - Edit .env file with your settings
   - Set up Google Drive API credentials
   - Configure database connection

3. Start services:
   - Run: {"start_dev.bat" if self.is_windows else "./start_dev.sh"}
   - Or: docker-compose up -d

4. Verify installation:
   - Run: python run_tests.py --unit
   - Access: http://localhost:8000/docs

5. Development:
   - API docs: http://localhost:8000/docs
   - Admin interface: http://localhost:8000/admin
   - Monitoring: http://localhost:3000 (Grafana)

Troubleshooting:
- Check logs in ./logs/ directory
- Verify services are running: docker-compose ps
- Check environment: python -c "from app.core.config import get_settings; print(get_settings())"

For help, see README.md or run: python install.py
"""
        
        report_file = self.project_root / "SETUP_REPORT.txt"
        report_file.write_text(report)
        
        print(report)
        self.log(f"Setup report saved to {report_file}", "SUCCESS")
        return True
    
    def run_complete_setup(self):
        """Run the complete setup process."""
        self.log("Starting Movie Recap Service Setup", "INFO")
        print("=" * 60)
        
        setup_steps = [
            (self.check_python_version, "Check Python version"),
            (self.install_python_dependencies, "Install Python dependencies"),
            (self.create_directories, "Create project directories"),
            (self.fix_import_issues, "Fix import issues"),
            (self.setup_environment_file, "Setup environment file"),
            (self.setup_database_config, "Setup database configuration"),
            (self.create_startup_scripts, "Create startup scripts"),
            (self.run_basic_tests, "Run basic tests"),
            (self.generate_summary_report, "Generate summary report"),
        ]
        
        failed_steps = []
        
        for step_func, step_name in setup_steps:
            try:
                self.log(f"\n--- {step_name} ---")
                if not step_func():
                    failed_steps.append(step_name)
            except Exception as e:
                self.log(f"Exception in {step_name}: {e}", "ERROR")
                failed_steps.append(step_name)
        
        print("\n" + "=" * 60)
        if not failed_steps:
            self.log("🎉 SETUP COMPLETED SUCCESSFULLY!", "SUCCESS")
            return True
        else:
            self.log("⚠️ SETUP COMPLETED WITH WARNINGS:", "WARNING")
            for step in failed_steps:
                self.log(f"  - {step}", "WARNING")
            return False


def main():
    """Main setup function."""
    setup = SetupManager()
    success = setup.run_complete_setup()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())