"""Measure real lookup/computation durations via Flask's local test client."""
import argparse
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db
from app.models import Collection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=30)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be a positive integer")
    app = create_app()
    with app.app_context():
        heritage = db.session.scalar(db.select(Collection).where(Collection.name == "Heritage", Collection.company == "ABC Paint"))
        horizon = db.session.scalar(db.select(Collection).where(Collection.name == "Horizon", Collection.company == "ABC Paint"))
        if heritage is None or horizon is None:
            parser.error("Run the seed command first.")
        source_id, target_id = heritage.id, horizon.id
    operations = {
        "Search": ("/search", {"mode": "name", "query": "harbor", "collection_id": 0}),
        "Translator": ("/translate", {"paint_number": "H001", "collection_id": source_id, "target_id": target_id}),
        "Closest": ("/closest", {"paint_number": "H001", "collection_id": source_id, "target_id": target_id, "scheme": "old", "count": 5}),
    }
    print(f"Real server operation timings in milliseconds, {args.runs} requests per operation.")
    print("Includes first request; excludes template rendering, request setup, and network transit.")
    with app.test_client() as client:
        for name, (path, parameters) in operations.items():
            times = []
            for _ in range(args.runs):
                response = client.get(path, query_string=parameters)
                if response.status_code != 200 or "X-Processing-Time-ms" not in response.headers:
                    raise SystemExit(f"{name} failed: status {response.status_code}; verify database setup.")
                times.append(float(response.headers["X-Processing-Time-ms"]))
            print(f"{name:12s} min={min(times):.4f}  mean={statistics.mean(times):.4f}  median={statistics.median(times):.4f}  max={max(times):.4f}")
    print("These observations support later evaluation; they are not an NFR pass/fail conclusion.")


if __name__ == "__main__":
    main()
