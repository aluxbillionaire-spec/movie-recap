#!/usr/bin/env python3
"""
Frontend setup and installation script.
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description, cwd=None):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr and "warn" not in result.stderr.lower():
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            return True
        else:
            print(f"❌ FAILED: {description}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Main setup function."""
    print("🎬 Movie Recap Service - Frontend Setup")
    print("="*50)
    
    frontend_dir = Path(__file__).parent
    
    # Check if Node.js is installed
    if not run_command("node --version", "Check Node.js installation"):
        print("\n❌ Node.js is not installed.")
        print("Please install Node.js 18+ from https://nodejs.org")
        return 1
    
    # Check if npm is installed
    if not run_command("npm --version", "Check npm installation"):
        print("\n❌ npm is not installed.")
        return 1
    
    # Install dependencies
    if not run_command("npm install", "Install dependencies", frontend_dir):
        print("\n❌ Failed to install dependencies.")
        return 1
    
    # Create environment file
    env_file = frontend_dir / ".env"
    env_example = frontend_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
    
    # Run type check
    run_command("npm run lint", "Run ESLint check", frontend_dir)
    
    # Build the project to verify everything works
    if run_command("npm run build", "Build project", frontend_dir):
        print("\n🎉 Frontend setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your configuration")
        print("2. Start development server: npm run dev")
        print("3. Open http://localhost:3000 in your browser")
        return 0
    else:
        print("\n❌ Build failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())