"""Deterministic validation of AI inference dependency resilience contracts."""

from __future__ import annotations

from datetime import date
from typing import Any


def _check(rule: str, passed: bool, message: str, severity: str = "BLOCK") -> dict[str, Any]:
    return {"rule": rule, "passed": passed, "severity": severity, "message": message}


def _all(deps: list[dict[str, Any]], predicate) -> bool:
    return bool(deps) and all(predicate(dep) for dep in deps)


def evaluate(document: dict[str, Any], policy: dict[str, Any], as_of: date | None = None) -> dict[str, Any]:
    """Return a stable PASS, REVIEW, or BLOCK decision for a resilience contract."""
    today = as_of or date.today()
    service = document.get("service", {})
    deps = document.get("dependencies", [])
    operations = document.get("operations", {})
    validation = document.get("validation", {})
    rules: list[dict[str, Any]] = []

    budget = service.get("request_budget_ms", 0)
    rules.append(_check("RG-001", bool(service.get("name")) and isinstance(budget, int) and budget > 0, "Named service has an end-to-end request budget"))

    slo = service.get("slo", {})
    rules.append(_check("RG-002", slo.get("availability_percent", 0) >= policy["minimum_availability_percent"] and bool(slo.get("error_budget_policy")), "Availability SLO and error-budget policy declared"))

    rules.append(_check("RG-003", service.get("deadline_propagation") is True and _all(deps, lambda d: 0 < d.get("timeout_ms", 0) < budget), "Deadlines propagate and dependency timeouts fit the request budget"))

    rules.append(_check("RG-004", _all(deps, lambda d: 1 <= d.get("retry", {}).get("max_attempts", 0) <= policy["max_attempts"] and d.get("retry", {}).get("backoff") == "exponential" and d.get("retry", {}).get("jitter") is True), "Retries are bounded with exponential backoff and jitter"))

    rules.append(_check("RG-005", _all(deps, lambda d: 0 <= d.get("retry", {}).get("budget_percent", 101) <= policy["max_retry_budget_percent"]), "Retry budgets limit amplification"))

    rules.append(_check("RG-006", _all(deps, lambda d: d.get("circuit_breaker", {}).get("failure_threshold", 0) > 0 and d.get("circuit_breaker", {}).get("open_seconds", 0) > 0 and d.get("circuit_breaker", {}).get("half_open_requests", 0) > 0), "Circuit breakers fail fast and probe recovery"))

    rules.append(_check("RG-007", _all(deps, lambda d: d.get("bulkhead", {}).get("max_concurrency", 0) > 0 and d.get("bulkhead", {}).get("max_queue", -1) >= 0), "Bulkhead concurrency and queue limits isolate failures"))

    rules.append(_check("RG-008", _all(deps, lambda d: d.get("rate_limit_rps", 0) > 0 and 0 < d.get("load_shed_percent", 0) <= 100 and d.get("backpressure") is True), "Rate limits, load shedding, and backpressure are configured"))

    critical = [d for d in deps if d.get("criticality") == "critical"]
    fallback = _all(critical, lambda d: bool(d.get("fallback", {}).get("provider")) and d.get("fallback", {}).get("provider") != d.get("provider") and bool(d.get("fallback", {}).get("model")))
    rules.append(_check("RG-009", bool(critical) and fallback, "Critical dependencies have distinct provider/model fallbacks"))

    rules.append(_check("RG-010", _all(deps, lambda d: d.get("idempotency_key") is True and d.get("request_deduplication") is True), "Retries are safe through idempotency and deduplication"))

    rules.append(_check("RG-011", _all(deps, lambda d: d.get("criticality") in {"critical", "degradable"} and d.get("health_probe", {}).get("enabled") is True and d.get("health_probe", {}).get("interval_seconds", 0) > 0), "Dependency criticality and health probes are explicit"))

    required_metrics = set(policy["required_metrics"])
    telemetry = service.get("telemetry", {})
    rules.append(_check("RG-012", required_metrics <= set(telemetry.get("metrics", [])) and telemetry.get("traces") is True and telemetry.get("dependency_attributes") is True, "OpenTelemetry evidence covers latency, errors, retries, breakers, and shedding"))

    operational = all(operations.get(k) for k in ("owner", "runbook", "alert_route", "dashboard"))
    rules.append(_check("RG-013", operational, "Owner, runbook, alert route, and dashboard recorded", "REVIEW"))

    chaos = validation.get("chaos_test", {})
    try:
        raw_last_run = chaos.get("last_run", "1900-01-01")
        last_run = raw_last_run if isinstance(raw_last_run, date) else date.fromisoformat(str(raw_last_run))
        chaos_age = (today - last_run).days
    except (TypeError, ValueError):
        chaos_age = 10**6
    rules.append(_check("RG-014", chaos.get("passed") is True and 0 <= chaos_age <= policy["max_chaos_age_days"] and set(chaos.get("scenarios", [])) >= {"timeout", "rate_limit", "provider_outage"}, "Fresh chaos evidence covers timeout, rate-limit, and provider outage"))

    load = validation.get("load_test", {})
    rules.append(_check("RG-015", load.get("passed") is True and load.get("p95_ms", budget + 1) < budget and load.get("success_percent", 0) >= slo.get("availability_percent", 100), "Load test meets latency and success targets"))

    rules.append(_check("RG-016", validation.get("capacity_headroom_percent", 0) >= policy["minimum_capacity_headroom_percent"], "Capacity headroom supports degraded operation"))

    privacy = service.get("privacy", {})
    allowed_regions = set(privacy.get("allowed_regions", []))
    privacy_ok = bool(allowed_regions) and _all(critical, lambda d: set(d.get("fallback", {}).get("regions", [])) <= allowed_regions and d.get("fallback", {}).get("data_classification") == privacy.get("data_classification"))
    rules.append(_check("RG-017", privacy_ok, "Fallbacks preserve data classification and residency"))

    canary = validation.get("canary", {})
    rules.append(_check("RG-018", canary.get("enabled") is True and 0 < canary.get("traffic_percent", 0) <= policy["max_canary_percent"] and canary.get("automatic_rollback") is True, "Canary validation and automatic rollback limit change risk"))

    failed = [rule for rule in rules if not rule["passed"]]
    decision = "BLOCK" if any(rule["severity"] == "BLOCK" for rule in failed) else "REVIEW" if failed else "PASS"
    score = round(100 * (len(rules) - len(failed)) / len(rules), 1)
    return {"decision": decision, "score": score, "passed": len(rules) - len(failed), "total": len(rules), "rules": rules}

