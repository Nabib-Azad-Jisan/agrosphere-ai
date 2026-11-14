"""Generate local secrets without printing them. Run after copying .env.example."""

from pathlib import Path
import secrets

path = Path(".env")
if not path.exists():
    path.write_text(Path(".env.example").read_text(encoding="utf-8"), encoding="utf-8")
lines = path.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if line in {"ADMIN_TOKEN=", "POSTGRES_PASSWORD="}:
        lines[index] = line + secrets.token_hex(24)
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Local configuration ready. Secrets remain in ignored .env.")
