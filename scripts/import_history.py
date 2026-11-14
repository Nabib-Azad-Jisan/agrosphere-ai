"""Import canonical JSONL without modifying original timestamps; requires registered device."""

import argparse
import os
import json
import httpx
from backend.app.adapters import HistoricalAdapter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--license", required=True, help="Dataset license and attribution")
    args = parser.parse_args()
    token = os.environ["DEVICE_TOKEN"]
    url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
    with open(args.path, encoding="utf-8") as handle, httpx.Client(timeout=15) as client:
        for line in handle:
            payload = HistoricalAdapter(json.loads(line)).read()
            response = client.post(f"{url}/readings", json=payload, headers={"X-Device-Token": token})
            response.raise_for_status()
    print(f"Imported measured observations. Attribution: {args.license}")


if __name__ == "__main__":
    main()
