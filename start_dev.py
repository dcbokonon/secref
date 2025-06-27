#!/usr/bin/env python3
"""
Simple development server launcher for SecRef
Starts both Astro and Flask admin panel
"""

import subprocess
import time
import os
import sys
import signal
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

processes = []

def cleanup(signum=None, frame=None):
    """Clean up processes on exit"""
    print(f"\n{YELLOW}Stopping services...{RESET}")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except:
            p.kill()
    print(f"{GREEN}✓ Services stopped{RESET}")
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def main():
    print(f"{BLUE}🚀 Starting SecRef Development Environment{RESET}")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("package.json").exists():
        print(f"{RED}Error: Run this from the SecRef root directory{RESET}")
        sys.exit(1)
    
    # Set up Python virtual environment if needed
    venv_path = Path("venv")
    if not venv_path.exists():
        print(f"{BLUE}Creating Python virtual environment...{RESET}")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Install admin requirements
        pip_path = venv_path / "bin" / "pip" if os.name != 'nt' else venv_path / "Scripts" / "pip"
        subprocess.run([str(pip_path), "install", "-q", "-r", "admin/requirements.txt"], check=True)
    
    # Start Astro
    print(f"\n{BLUE}Starting Astro development server...{RESET}")
    astro_process = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    processes.append(astro_process)
    
    # Start Flask admin
    print(f"{BLUE}Starting admin panel...{RESET}")
    
    # Activate venv and run Flask
    if os.name == 'nt':  # Windows
        activate_script = str(venv_path / "Scripts" / "activate.bat")
        flask_cmd = f'cmd /c "{activate_script} && cd admin && flask run"'
    else:  # Unix-like
        activate_script = f"source {venv_path}/bin/activate"
        flask_cmd = f'bash -c "{activate_script} && cd admin && flask run"'
    
    flask_process = subprocess.Popen(
        flask_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    processes.append(flask_process)
    
    # Give services time to start
    time.sleep(3)
    
    print(f"\n{GREEN}✅ Services started!{RESET}")
    print(f"\n{GREEN}📍 Astro Site:   {YELLOW}http://localhost:4321{RESET}")
    print(f"{GREEN}📍 Admin Panel:  {YELLOW}http://localhost:5001{RESET}")
    print(f"\n{YELLOW}Press Ctrl+C to stop all services{RESET}\n")
    
    # Monitor processes
    try:
        while True:
            # Check if processes are still running
            for p in processes:
                if p.poll() is not None:
                    print(f"{RED}A service has stopped unexpectedly!{RESET}")
                    cleanup()
            
            # Print output from Astro
            if astro_process.stdout:
                line = astro_process.stdout.readline()
                if line and "ready in" in line.lower():
                    print(f"{GREEN}✓ Astro ready!{RESET}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()