#!/usr/bin/env python3
"""
Setup script for UAV-UGV Rescue System
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")

def install_dependencies():
    """Install project dependencies"""
    print("📥 Installing dependencies...")
    
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
    else:  # Unix/Linux/macOS
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("🔧 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ .env file created")
        print("⚠️  Please update .env with your OpenAI API key")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 Setting up UAV-UGV Rescue System")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    create_env_file()
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your OpenAI API key")
    print("2. Run: python UAV_agent.py (to test UAV)")
    print("3. Run: python UGV_Agent.py (to test UGV)")
    print("4. Run: python multi_agent_system.py (for full system)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
