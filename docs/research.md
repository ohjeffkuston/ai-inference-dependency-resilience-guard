# Demand and technical validation — 2026-11-11

## Demand rationale

Production AI services are distributed systems with unusually expensive and rate-limited dependencies. Current SRE and AI-infrastructure openings repeatedly emphasize inference reliability, Kubernetes/cloud operations, observability, incident response, capacity, and distributed-systems failure handling. The recurring problem is not adding an AI chatbot; it is preventing provider degradation from becoming a user-visible cascade.

Representative current job requirements checked:

- [Cohere — Site Reliability Engineer, Inference Infrastructure](https://jobs.ashbyhq.com/cohere/1dcdd745-d7ca-46a8-8fd3-b3865426d4bd) — production inference, distributed systems, observability, and reliability; listed compensation $160,000–$260,000.
- [Runpod — Site Reliability Engineer](https://jobs.ashbyhq.com/runpod/1d6b700a-2c45-4eb2-b74d-2d930f89ab22) — AI cloud reliability, Kubernetes, incident response, and capacity; listed compensation $150,000–$200,000.
- [Perplexity — Site Reliability Engineer, Cloud Infrastructure](https://jobs.ashbyhq.com/perplexity/50b4d512-cd76-4baa-8885-396605d45cb7) — resilient cloud infrastructure and observability for AI products; listed compensation $220,000–$405,000.
- [OpenRouter — Site Reliability Engineer, Provider Operations](https://jobs.ashbyhq.com/openrouter/ce4bfd6a-c11e-4926-856a-f600307d37cb) — provider reliability, incident response, and operational automation; listed compensation $245,000–$295,000.

Postings are evidence of recurring capabilities, not an endorsement or an assertion that each role is eligible for the candidate. URLs and compensation can change.

## Authoritative technical sources

- [Google SRE: Service Best Practices](https://sre.google/sre-book/service-best-practices/) — deadlines, retries, load shedding, and overload controls.
- [Google SRE: Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) — retry amplification, queueing, and fail-fast behavior.
- [Google SRE: Handling Overload](https://sre.google/sre-book/handling-overload/) — request rejection, capacity protection, and graceful degradation.
- [Google SRE Workbook: Error Budget Policy](https://sre.google/workbook/error-budget-policy/) — using reliability evidence to constrain releases.
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) — reliability, failure isolation, and operational excellence.
- [AWS Cloud Design Patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/introduction.html) — retry, circuit breaker, bulkhead, and fallback patterns.
- [OpenTelemetry metric semantic conventions](https://opentelemetry.io/docs/specs/semconv/general/metrics/) — interoperable operational signals.
- [Kubernetes Pod Disruption Budgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) — controlling voluntary disruption; useful but not a substitute for dependency resilience.

## Scope decision

The project validates resilience contracts without sending live traffic or changing infrastructure. This keeps the demo deterministic and safe while making the production boundary explicit. Chaos execution, provider-specific breaker libraries, Kubernetes policy admission, and real SLO backends are integration points rather than simulated claims.
