from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest
import yaml

from inference_resilience_guard import evaluate

ROOT = Path(__file__).parents[1]
POLICY = yaml.safe_load((ROOT / "policy/resilience-policy.yaml").read_text())
GOOD = yaml.safe_load((ROOT / "samples/compliant-contract.yaml").read_text())
BAD = yaml.safe_load((ROOT / "samples/unsafe-contract.yaml").read_text())
AS_OF = date(2026, 11, 11)


def test_compliant_contract_passes_all_eighteen_checks():
    result = evaluate(GOOD, POLICY, AS_OF)
    assert result["decision"] == "PASS"
    assert result["score"] == 100.0
    assert result["passed"] == result["total"] == 18


def test_unsafe_contract_blocks():
    result = evaluate(BAD, POLICY, AS_OF)
    assert result["decision"] == "BLOCK"
    assert result["score"] < 20


@pytest.mark.parametrize(
    ("mutate", "rule"),
    [
        (lambda d: d["service"].update(deadline_propagation=False), "RG-003"),
        (lambda d: d["dependencies"][0]["retry"].update(max_attempts=9), "RG-004"),
        (lambda d: d["dependencies"][0]["retry"].update(budget_percent=50), "RG-005"),
        (lambda d: d["dependencies"][0]["circuit_breaker"].update(failure_threshold=0), "RG-006"),
        (lambda d: d["dependencies"][0]["bulkhead"].update(max_concurrency=0), "RG-007"),
        (lambda d: d["dependencies"][0].update(backpressure=False), "RG-008"),
        (lambda d: d["dependencies"][0]["fallback"].update(provider="provider-a"), "RG-009"),
        (lambda d: d["dependencies"][0].update(idempotency_key=False), "RG-010"),
        (lambda d: d["dependencies"][0]["health_probe"].update(enabled=False), "RG-011"),
        (lambda d: d["service"]["telemetry"].update(traces=False), "RG-012"),
        (lambda d: d["validation"]["chaos_test"].update(last_run="2025-01-01"), "RG-014"),
        (lambda d: d["validation"]["load_test"].update(p95_ms=3000), "RG-015"),
        (lambda d: d["validation"].update(capacity_headroom_percent=5), "RG-016"),
        (lambda d: d["dependencies"][0]["fallback"].update(regions=["eu-west-1"]), "RG-017"),
        (lambda d: d["validation"]["canary"].update(traffic_percent=50), "RG-018"),
    ],
)
def test_resilience_regressions_block(mutate, rule):
    candidate = deepcopy(GOOD)
    mutate(candidate)
    result = evaluate(candidate, POLICY, AS_OF)
    assert result["decision"] == "BLOCK"
    assert rule in {item["rule"] for item in result["rules"] if not item["passed"]}


def test_missing_operational_evidence_requires_review_only():
    candidate = deepcopy(GOOD)
    candidate["operations"].pop("runbook")
    result = evaluate(candidate, POLICY, AS_OF)
    assert result["decision"] == "REVIEW"
    assert result["score"] == 94.4

