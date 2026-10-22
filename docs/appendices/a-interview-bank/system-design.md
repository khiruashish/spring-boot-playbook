# System Design

Grocery-domain design problems with model answers. Each follows the same structure an interviewer expects: **clarify → estimate → design → deep dive → failure modes → trade-offs**. Model answers are outlines of what a strong candidate covers, with chapter references for depth — not scripts to recite.

## How to approach a design question

| Step | Time (45 min) | What good looks like |
|---|---|---|
| Clarify requirements | 5 min | Users, scale, consistency needs, SLOs, what's out of scope |
| Estimate | 3 min | Requests/s, data volume, peak multiplier — rough is fine |
| High-level design | 10 min | Services, data ownership, sync vs async, one diagram |
| Deep dive | 15 min | The hardest part, in detail: consistency, a hot path, a failure mode |
| Failure and operations | 7 min | What breaks, how it degrades, how you'd know |
| Trade-offs and evolution | 5 min | What you'd change at 10× or with more time |

Interviewers score **reasoning**, not diagrams. "We'd use Kafka" earns nothing; "events here because notification must not block checkout, keyed by order ref for ordering, with an outbox so the publish can't be lost" earns a lot.

---

## SD-1 · Checkout for an online grocery platform

**Prompt:** Design checkout: cart to confirmed order, including stock reservation and payment. Peak 3,000 orders/min during a sale.

??? success "Model answer outline"
    **Clarify**: Consistency for money and stock is strict; notifications and loyalty can lag. Checkout p99 < 2 s, availability 99.5%. Payments via an external gateway with webhooks.

    **Estimate**: 50 orders/s peak; ~4 API calls per order ≈ 200 req/s at checkout; each order ~5 lines → 250 reservations/s.

    **Design**:
    ```mermaid
    flowchart LR
        App --> GW[Gateway] --> O[order-service]
        O -->|price, before TX| P[pricing]
        O -->|TX: order + saga + outbox| DB[(orders DB)]
        DB -->|relay| K[(Kafka)]
        K --> I[inventory] --> K
        K --> PAY[payment] --> RZ[Gateway]
        RZ -->|signed webhook| PAY
        K --> N[notification]
    ```
    - Order created in one transaction with saga state and an outbox row; respond **201 PLACED** immediately.
    - Orchestrated saga: reserve stock → authorize payment → confirm. Deadlines, guarded transitions, compensations (release stock, void payment).
    - Idempotency key on the POST; inbox idempotency in every consumer.
    - Authoritative pricing fetched **before** the transaction, with timeout, breaker and cached-price degradation.

    **Deep dive — the saga**: persisted state with version for optimistic locking; out-of-order events counted and ignored; a timeout sweeper; STUCK after repeated compensation failure with a page.

    **Failure modes**: payment gateway down → 503 + Retry-After, sagas compensate at deadline; broker down → outbox accumulates, nothing lost; pricing slow → cached price flagged "may vary"; late payment after compensation → auto-void.

    **Operations**: SLO burn-rate alerts; open/stuck saga gauges; hourly reconciliation orders ↔ payments ↔ reservations.

    **Trade-offs**: 201 PLACED rather than synchronous PAID trades immediate certainty for availability and latency; polling outbox before CDC; orchestration over choreography for visibility.

    **Chapters**: 04, 16, 19, 23, 26, 36, 44.

---

## SD-2 · Product search with typo tolerance and facets

**Prompt:** 2 million SKUs, Indian vocabulary ("aata", "dahi"), filters by brand, price and pincode availability, facets, p95 < 400 ms.

??? success "Model answer outline"
    **Design**: PostgreSQL as source of truth; outbox events → indexer → OpenSearch behind an alias. Indexer loads projections from the source rather than trusting event payloads.

    **Mapping**: `text` fields with search-time synonyms (atta/aata/flour), fuzziness `AUTO`; `keyword` for brand/category; `scaled_float` for price; availability as a list of serviceable pincodes; popularity for boosting.

    **Query**: multi-match with field boosts; filters (not queries) for structured constraints; aggregations for facets; `search_after` with a unique tiebreaker for pagination.

    **Deep dive — reindexing**: new index with new mapping, bulk load, catch-up from Kafka offsets, golden-query validation, atomic alias swap, old index kept for rollback.

    **Failure modes**: cluster down → breaker + category browse from PostgreSQL; index lag alert; zero-result-rate alert as a quality signal.

    **Trade-offs**: eventual consistency (sellers see their own changes from the owner, not search); search-time synonyms trade query cost for no-reindex updates.

    **Chapters**: 22, 23, 26, 36.

---

## SD-3 · Live delivery tracking

**Prompt:** 8,000 riders ping location every 5 s; up to 40,000 customers watch their order's rider live.

??? success "Model answer outline"
    **Estimate**: 1,600 pings/s inbound; 40,000 long-lived outbound connections.

    **Design**: rider pings → ingest service (WebFlux) → Redis geo + pub/sub, sampled history to PostgreSQL via R2DBC; customers connect via **SSE** to a WebFlux stream service subscribed per rider.

    **Deep dive — backpressure**: live positions use `onBackpressureDrop` plus `sample(2s)` — stale positions are worthless and buffering per slow client is a memory leak; heartbeats every 20 s; idle timeout; `doFinally` cleanup; open-connection gauge as the capacity metric.

    **Security**: token validated at connect; ownership check that the order belongs to the customer; no rider PII beyond first name and position.

    **Failure modes**: rollout disconnects clients → SSE auto-reconnect; Redis blip → stream pauses, resumes; slow mobile networks → drops, not buffers.

    **Trade-offs**: SSE over WebSocket (push-only, automatic reconnect); WebFlux here specifically, MVC elsewhere.

    **Chapters**: 22, 31, 32.

---

## SD-4 · Rider dispatch

**Prompt:** Assign each packed order to exactly one nearby rider; express orders first; retry if nobody accepts within 30 s; never assign two riders.

??? success "Model answer outline"
    **Design**: RabbitMQ topic exchange with quorum queues per priority class; competing consumers; publisher confirms from an outbox; `prefetch` low for fair distribution.

    **Deep dive — exactly one rider**: rider claimed with `SELECT … FOR UPDATE SKIP LOCKED`; assignment row with a unique constraint on order; release the rider if the insert loses the race. Redelivery is harmless because the operation is idempotent.

    **Retry**: TTL queue + dead-letter back to the work exchange with an attempt header; park after N attempts and alert a human dispatch desk.

    **Rider channel**: WebSocket + STOMP with a broker relay so user destinations reach the right pod; heartbeats; authenticated CONNECT.

    **Failure modes**: rider pool exhausted → delayed retry; poison task → parked immediately; broker node loss → quorum queues.

    **Trade-offs**: RabbitMQ (per-message routing, priority, delay) over Kafka (replayable log) for this flow specifically.

    **Chapters**: 12, 24, 32.

---

## SD-5 · Multi-tenant white-label marketplace

**Prompt:** Offer the platform to regional chains: 400 small tenants and 3 large ones, strict isolation, per-tenant branding.

??? success "Model answer outline"
    **Model**: shared schema with `tenant_id` for the long tail; database per tenant for the three large ones; the same code via a routing connection provider.

    **Enforcement**: tenant from the token (validated against subdomain); `@TenantId`; forced RLS with transaction-local settings; tenant-aware cache keys by default; propagation through async, Kafka headers, outbound HTTP; scheduled jobs loop over tenants explicitly.

    **Deep dive — proof**: reflective leak suite over every repository plus native queries, pooled-connection reset, async and messaging tests, in every build.

    **Noisy neighbours**: per-tenant rate limits and quotas; statement timeouts; large tenants in their own cells.

    **Lifecycle**: onboarding as a saga; export and deletion driven by the service catalog with evidence reports.

    **Trade-offs**: shared schema is cheap but relies on enforcement layers; dedicated databases isolate but multiply migrations and connections.

    **Chapters**: 35, 36, 38, 39.

---

## SD-6 · Weekly seller settlement

**Prompt:** 14,000 sellers, 2.8 million order lines per week, commission and TDS, bank payout file; must be restartable and correct.

??? success "Model answer outline"
    **Design**: Spring Batch job run as a Kubernetes CronJob (`Forbid`, no automatic retry): validate → partitioned calculation by seller → aggregate → payout file → reconcile → publish via outbox.

    **Deep dive — correctness**: identifying parameters include the period; paging readers with unique sort keys; idempotent writes keyed by `(order_line_id, run_date)`; a reconciliation step that **fails the job** before producing a wrong file.

    **Parallelism**: partitions by seller groups balanced by volume, sized against database connections.

    **Operations**: metrics on durations and totals; alerts on failure, **missed runs**, and deviation from last week's totals; runbook for restart.

    **Security**: bank details field-encrypted; payout changes held 24 h after a bank-account change.

    **Chapters**: 33, 36, 39.

---

## SD-7 · Support assistant with order lookup

**Prompt:** An AI assistant answers "where is my order?" and policy questions, deflecting tickets without inventing answers.

??? success "Model answer outline"
    **Design**: tenant-scoped RAG over policies (pgvector) with a similarity threshold; tools for order status and recent orders; human handoff queue.

    **Deep dive — safety**: tools derive identity from the session, re-check ownership, are read-only and audited; retrieved content delimited in the user message; empty retrieval → handoff; refund or complaint language → escalation; output caps and per-tenant token quotas.

    **Resilience**: provider behind a breaker and bulkhead; fallback is a human.

    **Quality**: CI evaluation suite with golden, refusal, injection and authorization tests; metrics for deflection, escalation, cost per conversation.

    **Compliance**: minimize data sent to the provider; processing agreement; residency review.

    **Chapters**: 17, 26, 38, 39, 40.

---

## SD-8 · Platform upgrade programme

**Prompt:** Move 26 services from Boot 3.5 to Boot 4 within two quarters without incidents during Diwali.

??? success "Model answer outline"
    **Plan**: fix deprecations on 3.5; upgrade platform starters and BOM first with a compatibility matrix; pilot on a low-risk service; waves from supporting to core; core services outside the freeze window with canary on SLOs.

    **Deep dive — behaviour safety**: golden-file JSON tests, access matrix, contract tests, performance baselines, cross-version Kafka and cache compatibility (versioned cache namespaces).

    **Tracking**: readiness scorecard per service; fleet version dashboard; regressions attributed to the upgrade.

    **Separation**: adopt new Boot 4 features (API versioning, HTTP service groups) only after the upgrade is green.

    **Chapters**: 29, 30, 41, 42.

---

## SD-9 · Observability for the platform

**Prompt:** On-call engineers must answer "what's broken and since when?" in two minutes.

??? success "Model answer outline"
    **Signals**: metrics with common tags and cardinality guards; traces via OTLP with tail sampling keeping errors and slow requests; JSON logs with `traceId` and `tenantId`.

    **SLOs**: per critical journey with multi-window burn-rate alerts; every alert links a runbook and dashboard.

    **Dashboards**: SLO → traffic (RED) → dependencies (with breaker state and degradation counters) → resources (USE) → async (lag, DLT, outbox) → business metrics, with deploy annotations.

    **Business metrics**: orders/min vs last week — catching failures that look technically healthy.

    **Governance**: contract tests for metric names; quarterly cardinality and cost review.

    **Chapters**: 07, 27.

---

## SD-10 · Resilience for a slow dependency

**Prompt:** The pricing service's p99 jumps from 80 ms to 4 s every few days. Checkout must stay up.

??? success "Model answer outline"
    **Immediate**: timeout inside the checkout budget (600 ms), one retry with jitter for idempotent reads, bulkhead, breaker ignoring business exceptions and counting slow calls.

    **Degradation**: last-known price from Redis (≤ 15 min) flagged "may vary"; fail honestly if none exists; never invent prices.

    **Load protection**: priority load shedding — search before checkout.

    **Verification**: Toxiproxy latency chaos test asserting bounded checkout latency and breaker transitions.

    **Root cause**: profile pricing under load; likely query or pool contention; performance regression gate afterwards.

    **Chapters**: 19, 21, 26, 28, 34.

---

## Scoring rubric (B4)

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Requirements | Jumps to tech | Clarifies scale, consistency, SLOs | Identifies the business trade-off first |
| Data and consistency | One DB | Ownership per service | Consistency model justified per flow |
| Failure | Ignored | Timeouts, retries, idempotency | Degradation per dependency, reconciliation |
| Operations | None | Metrics and alerts | SLOs, runbooks, rollout and rollback |
| Trade-offs | States a choice | Compares options | Knows when they'd change their mind |
| Communication | Monologue | Structured | Checks understanding and adapts |

See Chapter 43 for calibrating interviewers.

---

[:material-arrow-left: B5 · 12–15+ years](b5-12-15-years.md) · [Rapid Fire :material-arrow-right:](rapid-fire.md)
