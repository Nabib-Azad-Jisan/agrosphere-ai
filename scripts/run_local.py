"""Run the local app, API and worker together. Ctrl+C stops the process groups."""

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--postgres", action="store_true", help="Use local Docker PostgreSQL via the portable pg8000 driver")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    values = {k: v for k, v in dotenv_values(root / ".env").items() if v is not None}
    env = {**os.environ, **values}
    if args.postgres:
        if not values.get("POSTGRES_PASSWORD"):
            raise SystemExit("Run python scripts/configure_local.py and start docker compose up -d db first.")
        env["DATABASE_URL"] = (
            f"postgresql+pg8000://{values.get('POSTGRES_USER', 'agrosphere')}:"
            f"{values['POSTGRES_PASSWORD']}@127.0.0.1:5432/{values.get('POSTGRES_DB', 'agrosphere')}"
        )
    env["API_BASE_URL"] = "http://127.0.0.1:8000/api/v1"
    env["BACKEND_URL"] = "http://127.0.0.1:8000"
    env["NEXT_TELEMETRY_DISABLED"] = "1"
    node_entry = root / "frontend/node_modules/next/dist/bin/next"
    if not node_entry.exists():
        raise SystemExit("Install frontend dependencies with npm ci in frontend/ first.")
    subprocess.run([sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"], env=env, check=True)
    subprocess.run([sys.executable, "-m", "backend.app.seed"], env=env, check=True)
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    processes = []
    try:
        for command, cwd in [
            ([sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"], root),
            ([sys.executable, "-m", "backend.app.worker"], root),
            (["node", str(node_entry), "dev", "--hostname", "127.0.0.1"], root / "frontend"),
        ]:
            processes.append(subprocess.Popen(command, cwd=cwd, env=env, **options))
        print("AgroSphere: http://127.0.0.1:3000 — press Ctrl+C to stop all three services.", flush=True)
        while all(p.poll() is None for p in processes):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            if process.poll() is None:
                if os.name == "nt":
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    os.killpg(process.pid, signal.SIGTERM)
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.terminate()


if __name__ == "__main__":
    main()
