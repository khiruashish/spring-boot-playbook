# B4 · 8–12 Years

Cross-service design, operations, trade-offs and platform decisions. A strong B4 candidate reasons across several teams' systems, states trade-offs unprompted, and knows how a design behaves in production at 9 p.m. during a sale.

## Architecture and boundaries

??? question "B4 · How do you decide service boundaries?"
    **Short answer:** From business capabilities and bounded contexts found in the domain language, aligned with team ownership and different change and scaling profiles — validated by asking whether the service can deploy alone, owns its data and avoids synchronous chatter with neighbours. **Ch 35, 37.**

??? question "B4 · Modular monolith or microservices for a new platform?"
    **Short answer:** Modular monolith with verified boundaries unless there is a concrete need for independent deployment, scaling or ownership. It keeps local transactions and cheap refactoring while the domain is being learned, and makes later extraction a refactor. **Ch 37.**

??? question "B4 · How do you assess whether a platform is a distributed monolith?"
    **Short answer:** Check for ordered deployments, shared schemas, synchronous depth per user action, lockstep shared-library upgrades, unversioned contracts and local development needing many services. Fix the shared database first. **Ch 35.**

??? question "B4 · When do you replicate data between services instead of calling?"
    **Short answer:** For display and read-heavy access where seconds of staleness are acceptable; call the owner synchronously when the value must be authoritative for a decision (prices at checkout, stock at reservation). **Ch 35, 36.**

??? question "B4 · How do you extract a service from a monolith safely?"
    **Short answer:** Modularize in place; stand up the service read-only; route reads through the gateway with shadow comparison; move table ownership and writes; have the monolith call or consume events; delete old code and revoke grants — each step reversible. **Ch 35, 37.**

??? question "B4 · How do you classify subdomains and what follows?"
    **Short answer:** Core (invest: rich models, hexagonal, strongest engineers), supporting (pragmatic), generic (buy or keep simple). It directs effort to where differentiation lives. **Ch 37.**

## Data consistency

??? question "B4 · Design consistency for checkout across five services."
    **Short answer:** Outbox per service; inbox idempotency per consumer; an orchestrated saga with persisted state, deadlines and compensations; immediate 201 with PLACED and asynchronous progression; read models for history; two-directional reconciliation hourly; dashboards for open and stuck sagas. **Ch 36.**

??? question "B4 · When do you fix the boundary instead of building a saga?"
    **Short answer:** When two services must change together to protect one invariant — merging the data into one service gives a local transaction and removes a class of failures. Sagas are for steps that genuinely belong to different capabilities. **Ch 36, 37.**

??? question "B4 · Polling outbox or CDC — how do you decide platform-wide?"
    **Short answer:** Polling as the default for simplicity; CDC for high-volume or latency-sensitive services when the team can operate Kafka Connect and replication slots safely. Record it in an ADR with a revisit trigger. **Ch 36, 43.**

??? question "B4 · What does a mature reconciliation strategy look like?"
    **Short answer:** Pairs reconciled on a cadence matched to financial risk, in both directions, windows excluding in-flight work, drift metrics with alerts, tickets instead of silent auto-repair for money, and drift causes reviewed as defects. **Ch 33, 36.**

## APIs and integration

??? question "B4 · How do you govern APIs across many services?"
    **Short answer:** A written standard, lint rules and spec diffing in CI, a platform library implementing errors, pagination and headers, contract tests with a deploy gate, SDK generation, and per-client version telemetry. **Ch 20, 28, 41.**

??? question "B4 · You must change a field used by a million installed apps. How?"
    **Short answer:** Never mutate meaning in place: add the new field, dual-populate, version the representation, migrate clients with telemetry-driven outreach, retire the old field after a sunset window; gateways can adapt the long tail. **Ch 20.**

??? question "B4 · How do you choose between REST, GraphQL, gRPC and messaging?"
    **Short answer:** REST for public and most internal APIs; a GraphQL BFF where clients aggregate many resources with varying needs; gRPC for high-volume internal hot paths with deadlines; events wherever the caller doesn't need the result now. Record each choice. **Ch 32, 35.**

??? question "B4 · Design a mobile BFF."
    **Short answer:** One service owning no data or business rules, aggregating concurrently with timeouts, breakers and partial-failure handling, batch loaders everywhere, persisted queries and limits, shared error codes, separate scaling, and contract tests with app teams. **Ch 32.**

??? question "B4 · How do you migrate 40 Feign clients?"
    **Short answer:** Interface by interface to HTTP interfaces behind ports, mapping decoders to status handlers and retryers to explicit policy, running both behind a flag with contract tests, then deleting Feign. **Ch 19, 42.**

## Messaging at platform scale

??? question "B4 · Design the event architecture for the order lifecycle."
    **Short answer:** Versioned topics keyed by order reference; outbox publishing; per-service consumer groups with inbox idempotency; classified error handling with DLTs and replay tooling; governed topic configs; schema evolution rules with contract tests; lag, DLT and outbox dashboards. **Ch 23, 36.**

??? question "B4 · How do you choose partition counts?"
    **Short answer:** From peak throughput over per-consumer throughput, plus headroom for parallelism and per-key ordering limits; growth reshuffles keys, so start generous but bounded by broker overhead. **Ch 23.**

??? question "B4 · Kafka, RabbitMQ or a database queue?"
    **Short answer:** Kafka for fan-out, replay and ordered throughput; RabbitMQ for routed work queues with priorities, delays and per-message acks; a PostgreSQL `SKIP LOCKED` queue for single-consumer, modest-volume work that must be transactional with your data. **Ch 23, 24.**

??? question "B4 · How do you migrate an incompatible event schema?"
    **Short answer:** New versioned topic; producers dual-publish; consumers migrate one by one; retire the old topic when its consumer groups are gone — measured from the broker. **Ch 23.**

## Security and tenancy

??? question "B4 · Design the token architecture for customers, staff, services and partners."
    **Short answer:** OTP + PKCE with rotating refresh tokens for customers; OIDC SSO with passkeys and MFA for staff; client credentials for services; signed webhooks for partners; audience-scoped short-lived tokens; centralized claim mapping; documented rotation and revocation. **Ch 18.**

??? question "B4 · Gateway or service — where is authentication enforced?"
    **Short answer:** Both: the gateway validates tokens and applies quotas; services re-validate and enforce authorization and ownership. Never trust injected identity headers. **Ch 17, 35.**

??? question "B4 · Design multi-tenancy for 500 tenants with a long tail."
    **Short answer:** Shared schema with `@TenantId` and forced RLS; tenant from the token; platform-provided propagation; tenant-aware cache keys by default; per-tier quotas; a leak suite in CI; dedicated databases or cells for the largest; catalog-driven export and deletion. **Ch 38.**

??? question "B4 · What are the costs of database-per-tenant at scale?"
    **Short answer:** Connection multiplication, N migrations with partial failures and version skew, N backup and monitoring targets, slower incident response and higher spend — justified for a handful of tenants, not hundreds. **Ch 38.**

??? question "B4 · Design the security architecture for a consumer platform."
    **Short answer:** Layered trust boundaries; consumer and staff identity separated; mTLS and NetworkPolicy internally; least-privilege DB users with RLS and field encryption; append-only audit; signed images with admission control; CI security gates; DSR workflows; rehearsed incident response. **Ch 39.**

??? question "B4 · How do you reduce PCI scope?"
    **Short answer:** Never let card data reach your servers — gateway-hosted or SDK card entry, tokens for repeat payments, signed webhooks and segmentation. **Ch 39.**

## Resilience, performance, operations

??? question "B4 · Define a resilience policy for a platform."
    **Short answer:** A per-dependency table of timeout, retry, breaker, bulkhead and degradation mode, implemented in a platform library, visible in metrics, chaos-tested, reviewed when SLAs change and referenced in runbooks. **Ch 26.**

??? question "B4 · Application resilience or service mesh?"
    **Short answer:** Mesh for transport: mTLS, connection timeouts, outlier ejection, traffic shifting. Application for semantics: idempotency-aware retries, fallbacks, error translation. Retries in exactly one layer. **Ch 26, 30.**

??? question "B4 · How do you prepare a platform for 5× traffic?"
    **Short answer:** Forecast per service, breakpoint tests per pod, a written capacity model for pods, connections, partitions and cache; open-model full-journey load tests at 1.5× with profiling; soak and spike tests; game days; pre-scaling; deploy freeze. **Ch 34, 44.**

??? question "B4 · A team wants to double the connection pool to fix latency. Response?"
    **Short answer:** Check pool `pending` and query durations first; pool waits usually mean slow queries or long transactions. Fix those, then size against database capacity — a bigger pool moves contention into the database. **Ch 12, 34.**

??? question "B4 · Design observability for 26 services."
    **Short answer:** Platform library with common tags, cardinality guards, SLO histograms and health conventions; OTLP to a collector doing tail sampling and redaction; templated dashboards with deploy annotations; SLOs per critical journey with burn-rate alerts and runbooks; contract tests for metric names. **Ch 27.**

??? question "B4 · How do you decide what to alert on?"
    **Short answer:** Symptoms users feel (SLO burn, business-metric drops) and conditions about to become user-visible (lag, backlog, saturation). Everything else is a dashboard. Every alert has an owner and a runbook. **Ch 27.**

??? question "B4 · Standardize Kubernetes configuration for 26 services."
    **Short answer:** A Helm library chart encoding probes, shutdown timing, security context, resources, PDB, spread, network policy and scrape annotations; per-service overrides; GitOps delivery; conformance checks; game days. **Ch 30.**

??? question "B4 · How do you run a Diwali sale operationally?"
    **Short answer:** Scheduled pre-scaling, verified connection and partition budgets, capacity raised in advance, deploy freeze, rehearsed rollback, staffed incident roles, degradation switches ready, SLO burn dashboards watched. **Ch 30, 43, 44.**

## Delivery and testing

??? question "B4 · Design the image pipeline for many services."
    **Short answer:** Layered images, SBOM, scan with a fixable-high/critical gate, sign with provenance, push by commit, deploy to staging by digest, contract and smoke gates, promote the same digest, weekly base rebuilds or rebases, and fleet dashboards. **Ch 29.**

??? question "B4 · Design the test strategy for 26 services."
    **Short answer:** Fast unit and slice tests; integration on real infrastructure with shared containers; contract tests with a broker gate; event golden files; shared ArchUnit rules; nightly mutation, performance, chaos and flake detection; a few owned end-to-end journeys reused as synthetic monitors. **Ch 15, 28.**

??? question "B4 · CI takes 40 minutes and people bypass it. What do you do?"
    **Short answer:** Measure, split fast and slow jobs, fix context and container sharing, parallelize, cache, move mutation and performance to nightly, delete redundant end-to-end tests, and defend a budget. **Ch 28.**

## Platform engineering and upgrades

??? question "B4 · What becomes a platform library?"
    **Short answer:** Cross-cutting concerns most services need, stable enough to standardize, with no business logic and a team to own it; extract on the third copy. **Ch 41.**

??? question "B4 · How do you govern platform libraries?"
    **Short answer:** Named owners, semantic versioning with N-1 support, changelogs and compatibility matrices, release checklists including back-off and native tests, and fleet version telemetry. **Ch 41.**

??? question "B4 · How do you run a Boot major upgrade across 26 services?"
    **Short answer:** Readiness phase (deprecations, blockers), platform libraries first, a pilot, waves from low-risk to core, canary with SLO analysis outside freeze windows, a readiness scorecard and dashboard, then cleanup. **Ch 42.**

??? question "B4 · How do you fund upgrade work against feature pressure?"
    **Short answer:** Make it continuous: a fixed quarterly allocation, automated dependency updates, and a dashboard translating support-window and CVE risk into business terms. **Ch 42, 43.**

## AI and leadership

??? question "B4 · Design a support assistant for a consumer platform."
    **Short answer:** Authenticated, tenant-scoped RAG with thresholds; read-only, session-scoped, audited tools; delimited context; handoff on empty retrieval; token quotas; breaker with human fallback; CI evaluation; cost and quality metrics; a feature flag; legal review of data flows. **Ch 40.**

??? question "B4 · How do you decide whether an AI feature should ship?"
    **Short answer:** Worst output and its control, a working non-AI fallback, budgets for cost and latency, measurable quality with regression detection, and a lawful data flow. Any unclear answer means not ready. **Ch 40.**

??? question "B4 · How do you set technical direction for several teams?"
    **Short answer:** A short strategy with honest diagnosis tied to business outcomes, a few explicit bets and non-goals, individual pre-alignment, paved roads that make it easy to follow, and visible progress metrics. **Ch 43.**

??? question "B4 · How do you govern architecture without becoming a bottleneck?"
    **Short answer:** Most decisions stay in teams; RFCs with deadlines only for cross-cutting or irreversible changes; standards enforced by libraries and CI; recorded, time-boxed exceptions. **Ch 43.**

??? question "B4 · How do you use delivery metrics without them being gamed?"
    **Short answer:** Measure systems, not people; discuss trends rather than targets; pair each metric with its counter-metric; use them to decide where to help. **Ch 43.**

---

[:material-arrow-left: B3 · 5–8 years](b3-5-8-years.md) · [B5 · 12–15+ years :material-arrow-right:](b5-12-15-years.md)
