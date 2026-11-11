"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

from .guard import evaluate


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an AI inference dependency resilience contract")
    parser.add_argument("document", type=Path)
    parser.add_argument("--policy", type=Path, default=Path("policy/resilience-policy.yaml"))
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", choices=("text", "json"), default="text")
    args = parser.parse_args()
    result = evaluate(yaml.safe_load(args.document.read_text()), yaml.safe_load(args.policy.read_text()), args.as_of)
    if args.output == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['decision']} | score={result['score']}% | {result['passed']}/{result['total']} checks passed")
        for rule in result["rules"]:
            print(f"{'PASS' if rule['passed'] else rule['severity']}: {rule['rule']} - {rule['message']}")
    return 0 if result["decision"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

