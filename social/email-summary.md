# Day 28 — AI Inference Dependency Resilience Guard

To: ohjeffkuston@yahoo.ca

I completed Day 28 of the Cloud + AI portfolio: a deterministic release gate that checks whether AI inference dependencies can fail without causing a cascade.

## Deployment summary

The project validates 18 controls across request deadlines, bounded retries, retry budgets, circuit breakers, bulkheads, rate limits, backpressure, load shedding, privacy-compatible fallbacks, idempotency, health probes, OpenTelemetry evidence, ownership, chaos/load validation, capacity headroom, and canary rollback. It is designed for report-only CI adoption first, followed by gradual enforcement after service-owner review. Load and chaos work must remain in isolated non-production environments, and all infrastructure-impacting actions retain human approval.

## What I learned

The most important design lesson is that retries, fallbacks, and circuit breakers must be evaluated as a system. A fallback that shares capacity or violates data residency is not resilient. Test evidence also needs an expiry date; a passing chaos run from months ago cannot justify today's release. Deterministic enforcement should remain separate from optional AI explanation so probabilistic output cannot bypass policy.

## Interview positioning

This project gives me a concrete story about cascading failures in AI infrastructure: the production risk, SLO and error-budget context, request-budget design, retry amplification, failure isolation, observability, privacy constraints, chaos/load evidence, and rollout trade-offs. The implementation demonstrates Python, policy-as-code, testing, CI, SRE thinking, and AI-platform operations rather than a generic AI demo.

Repository: https://github.com/ohjeffkuston/ai-inference-dependency-resilience-guard
