"""
Maker Circulars - Data Management Platform
Single Main Entry Point to run the entire application (Backend + Frontend).

Usage:
    python main.py
    python main.py --backend-only
"""

import os
import sys
import time
import shutil
import signal
import subprocess
import webbrowser
import urllib.request
import urllib.error

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
DATA_DIR = os.path.join(ROOT_DIR, "data")
UPLOADS_DIR = os.path.join(ROOT_DIR, "uploads")


def ensure_directories():
    """Ensure data and upload directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)


def check_node_installed() -> bool:
    """Check if node and npm are available in PATH."""
    return shutil.which("node") is not None and shutil.which("npm") is not None


def ensure_frontend_dependencies():
    """Ensure node_modules are installed in the frontend directory."""
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if not os.path.exists(node_modules):
        print("[SETUP] Installing frontend dependencies (npm install)...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        subprocess.run([npm_cmd, "install"], cwd=FRONTEND_DIR, check=True)
        print("[SETUP] Frontend dependencies installed successfully.")


def wait_for_backend(url="http://127.0.0.1:8000/api/health", timeout=30):
    """Wait for backend server to become responsive."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def main():
    """
    Main orchestration function:
    1. Prepares directories and dependencies
    2. Starts the Backend (FastAPI / Uvicorn)
    3. Starts the Frontend (Vite dev server)
    4. Opens the browser
    5. Gracefully handles shutdown on Ctrl+C
    """
    print("=" * 60)
    print("  MAKER CIRCULARS - Starting Application")
    print("=" * 60)

    # 1. Setup directories
    ensure_directories()

    # 2. Add ROOT_DIR to sys.path so backend package is importable
    if ROOT_DIR not in sys.path:
        sys.path.insert(0, ROOT_DIR)

    backend_only = "--backend-only" in sys.argv

    # 3. Check node/npm if running frontend
    if not backend_only:
        if not check_node_installed():
            print("[WARNING] Node.js / npm not found in PATH!")
            print("Running in backend-only mode on http://127.0.0.1:8000")
            backend_only = True
        else:
            ensure_frontend_dependencies()

    processes = []

    def shutdown(signum=None, frame=None):
        print("\n[STOPPING] Shutting down servers gracefully...")
        for proc in processes:
            try:
                if sys.platform == "win32":
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    proc.terminate()
            except Exception:
                pass
        print("[STOPPED] All servers stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        # Start Backend Server
        print("\n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ]
        backend_proc = subprocess.Popen(backend_cmd, cwd=ROOT_DIR)
        processes.append(backend_proc)

        # Wait for backend health check
        print("Waiting for backend API to be ready...")
        if wait_for_backend():
            print("[OK] Backend is healthy at http://localhost:8000")
        else:
            print("[INFO] Backend started, proceeding...")

        # Start Frontend Server if not backend_only
        if not backend_only:
            print("\n[2/2] Starting Frontend Dev Server on http://localhost:5173 ...")
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            frontend_proc = subprocess.Popen([npm_cmd, "run", "dev"], cwd=FRONTEND_DIR)
            processes.append(frontend_proc)

            print("\n" + "=" * 60)
            print("  APPLICATION STARTED SUCCESSFULLY!")
            print("=" * 60)
            print("  Frontend UI : http://localhost:5173")
            print("  Backend API : http://localhost:8000")
            print("  API Docs    : http://localhost:8000/docs")
            print("=" * 60)
            print("Press Ctrl+C at any time to stop all servers.\n")

            time.sleep(1.5)
            webbrowser.open("http://localhost:5173")
        else:
            print("\n" + "=" * 60)
            print("  BACKEND STARTED SUCCESSFULLY!")
            print("=" * 60)
            print("  Backend API : http://localhost:8000")
            print("  API Docs    : http://localhost:8000/docs")
            print("=" * 60)
            print("Press Ctrl+C at any time to stop the server.\n")

            webbrowser.open("http://localhost:8000/docs")

        # Keep main thread alive while child processes run
        while True:
            for proc in processes:
                exit_code = proc.poll()
                if exit_code is not None:
                    print(f"\n[INFO] A service exited with code {exit_code}.")
                    shutdown()
            time.sleep(1)

    except KeyboardInterrupt:
        shutdown()
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {e}")
        shutdown()


if __name__ == "__main__":
    main()
