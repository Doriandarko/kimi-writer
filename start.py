#!/usr/bin/env python3
"""
Kimi Multi-Agent Novel Writing System Launcher

Starts both backend and frontend servers simultaneously.
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Color codes for terminal output (works in VS Code terminal)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color):
    """Print colored message."""
    print(f"{color}{message}{Colors.RESET}")

def print_header():
    """Print startup header."""
    print_colored("\n" + "="*70, Colors.CYAN)
    print_colored("  Kimi Multi-Agent Novel Writing System", Colors.BOLD + Colors.CYAN)
    print_colored("="*70 + "\n", Colors.CYAN)

def check_env_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    if not env_file.exists():
        print_colored("⚠️  Warning: .env file not found!", Colors.YELLOW)
        print_colored("   Please create a .env file with your MOONSHOT_API_KEY", Colors.YELLOW)
        print_colored("   You can copy env.example to .env and add your key\n", Colors.YELLOW)
        response = input("   Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(0)

def check_dependencies():
    """Check if dependencies are installed."""
    print_colored("🔍 Checking dependencies...", Colors.BLUE)

    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        print_colored("   ✓ Backend dependencies installed", Colors.GREEN)
    except ImportError:
        print_colored("   ✗ Backend dependencies missing", Colors.RED)
        print_colored("   Run: pip install -r requirements.txt", Colors.YELLOW)
        sys.exit(1)

    # Check if frontend node_modules exists
    frontend_modules = Path("frontend/node_modules")
    if not frontend_modules.exists():
        print_colored("   ⚠️  Frontend dependencies not installed", Colors.YELLOW)
        print_colored("   Installing frontend dependencies...", Colors.BLUE)
        try:
            subprocess.run(
                ["npm", "install"],
                cwd="frontend",
                check=True
            )
            print_colored("   ✓ Frontend dependencies installed", Colors.GREEN)
        except subprocess.CalledProcessError:
            print_colored("   ✗ Failed to install frontend dependencies", Colors.RED)
            print_colored("   Please run: cd frontend && npm install", Colors.YELLOW)
            sys.exit(1)
    else:
        print_colored("   ✓ Frontend dependencies installed", Colors.GREEN)

def start_servers():
    """Start both backend and frontend servers."""
    processes = []

    try:
        print_colored("\n🚀 Starting servers...\n", Colors.BOLD + Colors.GREEN)

        # Start backend
        print_colored("📡 Starting backend server on http://localhost:8000", Colors.BLUE)
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("Backend", backend_process))
        print_colored("   ✓ Backend started (PID: {})".format(backend_process.pid), Colors.GREEN)

        # Give backend time to start
        time.sleep(2)

        # Start frontend
        print_colored("\n🎨 Starting frontend server on http://localhost:5173", Colors.BLUE)
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("Frontend", frontend_process))
        print_colored("   ✓ Frontend started (PID: {})".format(frontend_process.pid), Colors.GREEN)

        # Print success message
        print_colored("\n" + "="*70, Colors.GREEN)
        print_colored("  ✨ System ready!", Colors.BOLD + Colors.GREEN)
        print_colored("="*70, Colors.GREEN)
        print_colored("\n📍 Open your browser to: http://localhost:5173", Colors.BOLD + Colors.CYAN)
        print_colored("📚 API Documentation: http://localhost:8000/docs", Colors.CYAN)
        print_colored("\n💡 Press Ctrl+C to stop both servers\n", Colors.YELLOW)

        # Wait for processes
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print_colored("\n\n⏹️  Shutting down servers...", Colors.YELLOW)

    except Exception as e:
        print_colored(f"\n❌ Error starting servers: {e}", Colors.RED)
        sys.exit(1)

    finally:
        # Clean up processes
        for name, process in processes:
            try:
                print_colored(f"   Stopping {name}...", Colors.YELLOW)
                process.terminate()
                process.wait(timeout=5)
                print_colored(f"   ✓ {name} stopped", Colors.GREEN)
            except subprocess.TimeoutExpired:
                print_colored(f"   Force killing {name}...", Colors.RED)
                process.kill()
            except Exception as e:
                print_colored(f"   Error stopping {name}: {e}", Colors.RED)

        print_colored("\n👋 Goodbye!\n", Colors.CYAN)

def main():
    """Main entry point."""
    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Print header
    print_header()

    # Check environment
    check_env_file()

    # Check dependencies
    check_dependencies()

    # Start servers
    start_servers()

if __name__ == "__main__":
    main()
