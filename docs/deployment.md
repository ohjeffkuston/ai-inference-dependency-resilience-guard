# Safe deployment guide

## 1. Establish the baseline

Inventory model providers, vector stores, rerankers, filters, and other request-path dependencies. Measure real latency, error, throttle, and retry behavior before setting thresholds. Define a service SLO and an error-budget policy.

## 2. Adopt in audit mode

Commit one contract per service and run the CLI in CI without blocking releases. Review findings with service owners. Keep evidence links and policy changes under code review.

## 3. Validate behavior safely

Run load and chaos experiments only in an isolated non-production environment with spend, concurrency, duration, and blast-radius limits. Exercise timeouts, provider rate limits, total provider loss, slow recovery, and fallback saturation. Verify privacy and residency on the fallback path.

## 4. Enforce gradually

Promote high-confidence BLOCK controls first. Treat missing operational metadata as REVIEW until ownership is clear. Deploy breaker or fallback changes via a small canary with automatic rollback. Do not let this repository perform production mutations.

## 5. Operate continuously

Export request duration, dependency errors, retry count, circuit state, shed count, queue saturation, and fallback use through OpenTelemetry. Alert on SLO burn rather than isolated symptoms. Expire chaos evidence and revalidate after dependency, model, region, or policy changes.

## Rollback

Rollback the application/configuration change, not the evidence gate. If the guard itself produces an unexpected result, pin the prior reviewed version, retain CI logs, and investigate before resuming enforcement. A bypass must be time-limited, owner-approved, and recorded.
