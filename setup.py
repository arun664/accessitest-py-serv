import os
import sys
import subprocess
from pathlib import Path

def create_virtualenv(env_name="venu"):
    """Create a virtual environment."""
    env_path = Path(env_name)
    if not env_path.exists():
        print(f"Creating virtual environment '{env_name}'...")
        subprocess.check_call([sys.executable, "-m", "venv", env_name])
    else:
        print(f"Virtual environment '{env_name}' already exists.")

def install_requirements(env_name="venu"):
    """Install requirements from requirements.txt in the virtual environment."""
    env_bin = Path(env_name) / "Scripts"  # This is specific to Windows
    pip_executable = env_bin / "pip.exe"  # Pip executable on Windows
    requirements_file = Path("requirements.txt")

    if requirements_file.exists():
        print(f"Installing requirements from {requirements_file}...")
        subprocess.check_call([pip_executable, "install", "-r", str(requirements_file)])
    else:
        print("Error: requirements.txt not found. Please ensure it exists in the same directory.")

if __name__ == "__main__":
    env_name = "venu"
    create_virtualenv(env_name)
    install_requirements(env_name)
    print(f"\nSetup complete! Activate the virtual environment with:\n")
    print(f"  {env_name}\\Scripts\\activate")
