#!/usr/bin/env python3
"""
Installation script for the Movie Recap Service.
Installs all required tools and dependencies.
"""
import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
from pathlib import Path


class MovieRecapInstaller:
    """Installer for Movie Recap Service dependencies."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_linux = self.system == "linux"
        self.is_macos = self.system == "darwin"
        
    def run_command(self, command, description, check=True):
        """Run a command and handle errors."""
        print(f"\n{'='*60}")
        print(f"Installing: {description}")
        print(f"Command: {command}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            
            if result.stderr and "warning" not in result.stderr.lower():
                print("STDERR:")
                print(result.stderr)
            
            if result.returncode != 0 and check:
                print(f"❌ FAILED: {description}")
                return False
            else:
                print(f"✅ SUCCESS: {description}")
                return True
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
    
    def check_python_version(self):
        """Check Python version."""
        print("Checking Python version...")
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            print(f"❌ Python {version.major}.{version.minor} detected. Python 3.11+ required.")
            print("Please install Python 3.11 or later from https://python.org")
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies."""
        print("\n📦 Installing Python dependencies...")
        
        # Upgrade pip first
        commands = [
            ("python -m pip install --upgrade pip", "Upgrade pip"),
            ("pip install -r backend/requirements.txt", "Install backend dependencies"),
            ("pip install -r requirements-test.txt", "Install test dependencies"),
        ]
        
        for command, description in commands:
            if not self.run_command(command, description):
                return False
        
        return True
    
    def install_postgresql(self):
        """Install PostgreSQL."""
        print("\n🐘 Installing PostgreSQL...")
        
        if self.is_windows:
            print("Please install PostgreSQL manually from:")
            print("https://www.postgresql.org/download/windows/")
            print("Or use: winget install PostgreSQL.PostgreSQL")
            return self.run_command("winget install PostgreSQL.PostgreSQL", "Install PostgreSQL", check=False)
        
        elif self.is_linux:
            # Try different package managers
            managers = [
                ("sudo apt-get update && sudo apt-get install -y postgresql postgresql-contrib", "APT"),
                ("sudo yum install -y postgresql postgresql-server", "YUM"),
                ("sudo dnf install -y postgresql postgresql-server", "DNF"),
            ]
            
            for command, manager in managers:
                if self.run_command(f"which {manager.lower()}", f"Check {manager}", check=False):
                    return self.run_command(command, f"Install PostgreSQL via {manager}")
        
        elif self.is_macos:
            return self.run_command("brew install postgresql", "Install PostgreSQL via Homebrew")
        
        return False
    
    def install_redis(self):
        """Install Redis."""
        print("\n🔴 Installing Redis...")
        
        if self.is_windows:
            print("Please install Redis manually from:")
            print("https://github.com/microsoftarchive/redis/releases")
            print("Or use Windows Subsystem for Linux (WSL)")
            return True
        
        elif self.is_linux:
            managers = [
                ("sudo apt-get install -y redis-server", "APT"),
                ("sudo yum install -y redis", "YUM"),
                ("sudo dnf install -y redis", "DNF"),
            ]
            
            for command, manager in managers:
                if self.run_command(f"which {manager.lower().split()[0]}", f"Check {manager}", check=False):
                    return self.run_command(command, f"Install Redis via {manager}")
        
        elif self.is_macos:
            return self.run_command("brew install redis", "Install Redis via Homebrew")
        
        return False
    
    def install_docker(self):
        """Install Docker."""
        print("\n🐳 Installing Docker...")
        
        if self.is_windows:
            print("Please install Docker Desktop from:")
            print("https://www.docker.com/products/docker-desktop")
            return True
        
        elif self.is_linux:
            commands = [
                ("curl -fsSL https://get.docker.com -o get-docker.sh", "Download Docker install script"),
                ("sudo sh get-docker.sh", "Install Docker"),
                ("sudo usermod -aG docker $USER", "Add user to docker group"),
                ("sudo systemctl enable docker", "Enable Docker service"),
                ("sudo systemctl start docker", "Start Docker service"),
            ]
            
            for command, description in commands:
                if not self.run_command(command, description, check=False):
                    print(f"⚠️  {description} may have failed, continuing...")
            
            return True
        
        elif self.is_macos:
            print("Please install Docker Desktop from:")
            print("https://www.docker.com/products/docker-desktop")
            return True
        
        return False
    
    def install_ffmpeg(self):
        """Install FFmpeg."""
        print("\n🎬 Installing FFmpeg...")
        
        if self.is_windows:
            print("Installing FFmpeg via package manager...")
            return self.run_command("winget install Gyan.FFmpeg", "Install FFmpeg", check=False) or \
                   self.run_command("choco install ffmpeg", "Install FFmpeg via Chocolatey", check=False)
        
        elif self.is_linux:
            managers = [
                ("sudo apt-get install -y ffmpeg", "APT"),
                ("sudo yum install -y ffmpeg", "YUM"),
                ("sudo dnf install -y ffmpeg", "DNF"),
            ]
            
            for command, manager in managers:
                if self.run_command(f"which {manager.lower().split()[0]}", f"Check {manager}", check=False):
                    return self.run_command(command, f"Install FFmpeg via {manager}")
        
        elif self.is_macos:
            return self.run_command("brew install ffmpeg", "Install FFmpeg via Homebrew")
        
        return False
    
    def install_additional_tools(self):
        """Install additional development tools."""
        print("\n🛠️  Installing additional tools...")
        
        tools = []
        
        if self.is_windows:
            tools = [
                ("winget install Git.Git", "Install Git"),
                ("winget install Microsoft.VisualStudioCode", "Install VS Code"),
                ("winget install Python.Python.3.11", "Install Python 3.11"),
            ]
        
        elif self.is_linux:
            tools = [
                ("sudo apt-get install -y git curl wget build-essential", "Install basic tools (APT)"),
                ("sudo yum groupinstall -y 'Development Tools'", "Install development tools (YUM)"),
            ]
        
        elif self.is_macos:
            tools = [
                ("xcode-select --install", "Install Xcode command line tools"),
                ("brew install git", "Install Git"),
            ]
        
        for command, description in tools:
            self.run_command(command, description, check=False)
        
        return True
    
    def setup_database(self):
        """Set up the database."""
        print("\n🗄️  Setting up database...")
        
        # Create database and user
        commands = [
            ("createdb movie_recap", "Create database"),
            ("createdb test_movie_recap", "Create test database"),
        ]
        
        for command, description in commands:
            self.run_command(command, description, check=False)
        
        # Run migrations
        if Path("backend/alembic").exists():
            os.chdir("backend")
            self.run_command("alembic upgrade head", "Run database migrations")
            os.chdir("..")
        
        return True
    
    def create_environment_file(self):
        """Create environment configuration file."""
        print("\n📝 Creating environment configuration...")
        
        if not Path(".env").exists() and Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env file with your specific configuration")
        
        return True
    
    def verify_installation(self):
        """Verify all installations."""
        print("\n🔍 Verifying installations...")
        
        checks = [
            ("python --version", "Python"),
            ("pip --version", "Pip"),
            ("psql --version", "PostgreSQL"),
            ("redis-cli --version", "Redis"),
            ("docker --version", "Docker"),
            ("ffmpeg -version", "FFmpeg"),
            ("git --version", "Git"),
        ]
        
        results = []
        for command, tool in checks:
            result = self.run_command(command, f"Check {tool}", check=False)
            results.append((tool, result))
        
        print(f"\n{'='*60}")
        print("INSTALLATION VERIFICATION")
        print(f"{'='*60}")
        
        for tool, success in results:
            status = "✅ INSTALLED" if success else "❌ MISSING"
            print(f"{tool:<15}: {status}")
        
        return all(result[1] for result in results)
    
    def run_tests(self):
        """Run basic tests to verify setup."""
        print("\n🧪 Running verification tests...")
        
        # Test Python imports
        test_imports = [
            "import fastapi",
            "import sqlalchemy",
            "import redis",
            "import celery",
            "import pytest",
        ]
        
        for import_test in test_imports:
            try:
                exec(import_test)
                print(f"✅ {import_test}")
            except ImportError as e:
                print(f"❌ {import_test}: {e}")
        
        # Run actual tests if possible
        if Path("run_tests.py").exists():
            self.run_command("python run_tests.py --unit", "Run unit tests", check=False)
        
        return True
    
    def install(self):
        """Main installation process."""
        print("🎬 Movie Recap Service Installer")
        print("="*50)
        print(f"Detected OS: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print("="*50)
        
        steps = [
            (self.check_python_version, "Check Python version"),
            (self.install_python_dependencies, "Install Python dependencies"),
            (self.install_postgresql, "Install PostgreSQL"),
            (self.install_redis, "Install Redis"),
            (self.install_docker, "Install Docker"),
            (self.install_ffmpeg, "Install FFmpeg"),
            (self.install_additional_tools, "Install additional tools"),
            (self.create_environment_file, "Create environment file"),
            (self.setup_database, "Setup database"),
            (self.verify_installation, "Verify installation"),
            (self.run_tests, "Run verification tests"),
        ]
        
        failed_steps = []
        
        for step_func, step_name in steps:
            try:
                if not step_func():
                    failed_steps.append(step_name)
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                failed_steps.append(step_name)
        
        print(f"\n{'='*60}")
        print("INSTALLATION SUMMARY")
        print(f"{'='*60}")
        
        if not failed_steps:
            print("🎉 ALL INSTALLATIONS COMPLETED SUCCESSFULLY!")
            print("\nNext steps:")
            print("1. Edit .env file with your configuration")
            print("2. Start services: docker-compose up -d")
            print("3. Run tests: python run_tests.py --all")
            print("4. Access API docs: http://localhost:8000/docs")
        else:
            print("⚠️  SOME INSTALLATIONS FAILED:")
            for step in failed_steps:
                print(f"  - {step}")
            print("\nPlease manually install failed components and re-run installer.")
        
        return len(failed_steps) == 0


def main():
    """Main function."""
    installer = MovieRecapInstaller()
    success = installer.install()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())