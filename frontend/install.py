"""
Frontend Installation Script
Automates npm installation and setup
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def run_command(command, description, cwd=None):
    """Run a shell command"""
    print(f"▶ {description}")
    print(f"  Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        print(f"  ✅ Success")
        if result.stdout:
            print(f"  Output: {result.stdout[:200]}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed: {e}")
        if e.stderr:
            print(f"  Error: {e.stderr[:200]}")
        return False


def main():
    """Main installation process"""
    print_header("ShizishanGPT React Frontend - Installation")
    
    # Get frontend directory
    frontend_dir = Path(__file__).parent
    
    print(f"Frontend directory: {frontend_dir}")
    
    # Check Node.js
    print_header("Checking Prerequisites")
    
    print("Checking Node.js...")
    success = run_command("node --version", "Checking Node.js version")
    
    if not success:
        print("  ❌ Node.js not found")
        print("  Please install Node.js from https://nodejs.org/")
        return
    
    print("Checking npm...")
    success = run_command("npm --version", "Checking npm version")
    
    if not success:
        print("  ❌ npm not found")
        return
    
    # Install dependencies
    print_header("Installing Dependencies")
    
    success = run_command(
        "npm install",
        "Installing React dependencies",
        cwd=frontend_dir
    )
    
    if not success:
        print("\n⚠️  Installation failed. Try manually:")
        print("   cd frontend")
        print("   npm install")
        return
    
    # Check .env file
    print_header("Checking Configuration")
    
    env_file = frontend_dir / ".env"
    if env_file.exists():
        print("  ✅ .env file exists")
    else:
        print("  ℹ️  Creating .env file...")
        env_content = """# React Frontend Configuration
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_NAME=ShizishanGPT
REACT_APP_VERSION=1.0.0
"""
        env_file.write_text(env_content)
        print("  ✅ .env file created")
    
    # Summary
    print_header("Installation Summary")
    
    print("✅ Node.js and npm verified")
    print("✅ Dependencies installed")
    print("✅ Configuration checked")
    
    print("\n" + "=" * 60)
    print("  🎉 Frontend Installation Complete!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Ensure Node.js middleware is running (port 5000)")
    print("  2. Ensure FastAPI backend is running (port 8000)")
    print("  3. Start the React frontend:")
    print("     cd frontend")
    print("     npm start")
    print("  4. Open http://localhost:3000 in your browser")
    print("\n")
    
    # Ask to start
    try:
        response = input("Would you like to start the development server now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            print("\nStarting React development server...")
            print("Server will open at http://localhost:3000")
            print("Press Ctrl+C to stop the server")
            
            subprocess.run(
                "npm start",
                shell=True,
                cwd=frontend_dir
            )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\nCouldn't start server automatically: {e}")
        print("Please run 'npm start' manually in the frontend directory")


if __name__ == "__main__":
    main()
