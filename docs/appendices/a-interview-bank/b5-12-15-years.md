# B5 · 12–15+ Years

Strategy, organization, risk, and knowing when *not* to use something. A strong B5 candidate reasons about the organization as a system: how technical choices shape teams, cost and risk over years, and how to move a large estate without breaking it.

## Strategy and architecture

??? question "B5 · When would you advise against microservices?"
    **Short answer:** Small teams, unclear domains, modest scale, or no operational capability for CI/CD, observability and on-call. A well-modularized monolith delivers most benefits at far lower cost and keeps the option to split later. **Ch 35, 37.**

??? question "B5 · How does organizational design shape service architecture?"
    **Short answer:** Conway's law: systems mirror communication structures. Long-lived teams owning capabilities produce clean boundaries; services split across teams, or teams owning many unrelated services, produce coupling regardless of technology. **Ch 35, 43.**

??? question "B5 · What does DDD actually buy an organization?"
    **Short answer:** A shared language between business and engineering, and boundaries aligned with how the business changes — so changes stay local. The strategic work matters more than the tactical patterns. **Ch 37.**

??? question "B5 · When is DDD the wrong investment?"
    **Short answer:** Simple CRUD systems, short-lived projects, generic subdomains, or no access to domain experts. Tactical patterns without strategic understanding produce ceremony without benefit. **Ch 37.**

??? question "B5 · How do you decide whether a new datastore or broker is justified?"
    **Short answer:** Demonstrate that the workload doesn't fit what you run, accept the operational cost (backups, upgrades, on-call, security review), confirm data can be rebuilt, and default to extending what exists. **Ch 22, 24.**

??? question "B5 · What's your position on forwarding user tokens between services?"
    **Short answer:** Avoid it — it spreads user credentials and makes every service a confused deputy. Use service identity plus explicit user context, and token exchange only where true delegation is required. **Ch 18.**

## Consistency, data and risk

??? question "B5 · What's the real cost of eventual consistency?"
    **Short answer:** It spreads beyond engineering: product designs pending states, support explains delays, finance accepts reconciliation windows, operations monitors drift. The organizational agreement on acceptable inconsistency is the hard part. **Ch 36.**

??? question "B5 · How do you keep distributed-data complexity from compounding?"
    **Short answer:** Boundaries that keep invariants local; a small set of standardized patterns in platform libraries; no ad-hoc variants; reconciliation for every cross-service invariant; saga count reviewed as an architectural health metric. **Ch 36, 41.**

??? question "B5 · What's the biggest risk in financial batch processing?"
    **Short answer:** Silent wrongness — jobs that succeed with bad numbers. Mitigate with reconciliation steps, business-total monitoring, dual controls on payout artifacts, immutable audit and rehearsed restarts. **Ch 33.**

??? question "B5 · Is batch processing obsolete in an event-driven architecture?"
    **Short answer:** No. Settlements, reconciliation, regulatory reporting and bulk corrections need point-in-time consistency, restartability and auditable artifacts. Events keep things current; batch proves they're correct. **Ch 33.**

## Reliability and operations

??? question "B5 · How does resilience relate to SLOs and error budgets?"
    **Short answer:** Resilience turns dependency failures into degraded successes, protecting availability; degradation must be measured separately so the organization distinguishes healthy, degraded and down, and budget burn directs investment to the weakest dependency. **Ch 26, 27.**

??? question "B5 · How does observability change engineering culture?"
    **Short answer:** It replaces opinion with evidence: SLOs align product and engineering, error budgets fund reliability work, reviews start from data, and instrumentation becomes part of "done". **Ch 27.**

??? question "B5 · When is Kubernetes the wrong choice?"
    **Short answer:** Small estates a managed PaaS covers, teams without capacity for cluster operations, or workloads better served by serverless. It pays off with many services, varied scaling and a platform team. **Ch 30.**

??? question "B5 · How do packaging choices affect reliability?"
    **Short answer:** Startup time bounds how fast you scale during incidents; image size bounds rollback speed; digest promotion determines trust in what's running; base-image hygiene sets exposure windows. They are reliability decisions disguised as build configuration. **Ch 29.**

??? question "B5 · How do you build performance into engineering culture?"
    **Short answer:** Budgets in design, load tests and profiles as normal deliverables, regression gates in CI, owned capacity models, incident reviews producing performance actions, and visible cost of decisions. **Ch 34.**

??? question "B5 · When is 'good enough' performance the right answer?"
    **Short answer:** When budgets are met with adequate headroom at forecast peak; beyond that, effort returns less than features or reliability work. **Ch 34.**

## Security, compliance, AI

??? question "B5 · How do you prioritize security investment?"
    **Short answer:** By risk across trust boundaries, informed by threat models and incident history. The highest returns are usually supply chain, staff access and authorization correctness — not exotic attacks. **Ch 39.**

??? question "B5 · What does a healthy security culture look like?"
    **Short answer:** Engineers threat model as part of design, secure defaults are the easy path, findings are defects with owners, incidents produce blameless reviews, and raising concerns is rewarded. **Ch 39, 43.**

??? question "B5 · How does multi-tenancy affect business economics?"
    **Short answer:** Isolation is a pricing tier: shared schema keeps small tenants nearly free; dedicated databases and cells carry real cost and must be sold accordingly, or engineering absorbs costs the contract never covered. **Ch 38.**

??? question "B5 · What's the hardest part of multi-tenancy?"
    **Short answer:** Sustained discipline — every feature, query, cache, job and integration can leak. Platform defaults, database-level enforcement and automated leak tests make correctness independent of memory. **Ch 38.**

??? question "B5 · Where should AI not be used?"
    **Short answer:** Decisions needing determinism, explainability or legal defensibility — pricing, refunds, fraud, credit, anything binding — plus latency-critical paths and problems where rules or conventional models do better. The strategy includes an explicit "not here" list. **Ch 40.**

??? question "B5 · What's the biggest organizational risk with AI features?"
    **Short answer:** Shipping demos without engineering discipline — no evaluation, cost controls, tool authorization or fallback — treating a non-deterministic remote dependency as a library call. **Ch 40.**

## Platform, upgrades, protocols

??? question "B5 · What's the cost of a platform abstraction?"
    **Short answer:** Support burden, release cadence, upgrade dependency and a learning curve. Worth it when it removes real duplication and enforces correctness; harmful when it thinly wraps a library or removes decisions teams should make. **Ch 41.**

??? question "B5 · How do you avoid a platform team becoming a bottleneck?"
    **Short answer:** Small, overridable libraries; no lockstep upgrades; N-1 support; contributions from service teams; deleting what's unused. A platform that says "wait for our release" too often gets routed around. **Ch 41.**

??? question "B5 · What does a healthy upgrade culture look like?"
    **Short answer:** Upgrades are boring — small, frequent, automated, measured and owned — with tests trusted enough that teams upgrade without fear. **Ch 42.**

??? question "B5 · When would you let a system stay on an old version?"
    **Short answer:** When retirement is near, exposure is isolated and upgrade cost exceeds residual risk — recorded, time-bound and revisited. Indefinite exceptions are how estates fall three majors behind. **Ch 42.**

??? question "B5 · What are the hidden costs of GraphQL?"
    **Short answer:** Runtime cost control, a new caching model, schema governance across teams, observability and rate limiting that don't come free, and the risk of a BFF accumulating business logic. **Ch 32.**

??? question "B5 · How do you avoid protocol sprawl?"
    **Short answer:** REST by default, a documented reason and owner for anything else, platform support for the sanctioned few, and periodic review of whether each non-REST interface still earns its complexity. **Ch 32.**

??? question "B5 · Does reactive still matter after virtual threads?"
    **Short answer:** Yes, for a narrower set: streaming with backpressure, connection-dense workloads and cancellation-heavy composition. For request/response services, MVC on virtual threads is the simpler default. **Ch 25, 31.**

## Leadership and organization

??? question "B5 · What distinguishes a principal engineer's impact?"
    **Short answer:** Multiplying others — direction many teams follow willingly, leverage through platforms, standards and people, expensive mistakes prevented, and an organization better able to change safely, measured over years. **Ch 43.**

??? question "B5 · How do you handle a strong disagreement with another senior leader?"
    **Short answer:** Understand their goals and constraints, find shared outcomes, bring data, experiment on reversible parts, escalate only with a clearly framed decision, and commit fully once made. **Ch 43.**

??? question "B5 · How do you know an engineering organization is healthy?"
    **Short answer:** Delivery metrics improving, incidents rarer and shorter, upgrades routine, standards adopted willingly, engineers growing and staying, cost per unit of value stable or falling, and people raising concerns early. **Ch 43.**

??? question "B5 · How do you keep architecture from eroding over years?"
    **Short answer:** Mechanical enforcement (ArchUnit, Modulith verification, contract gates, starters), generated documentation, ADRs with revisit triggers, clear ownership, and periodic context-map reviews against how the business actually changes. **Ch 37, 41, 43.**

??? question "B5 · How do you prevent broker, database and framework sprawl across teams?"
    **Short answer:** A decision guide, platform support for the sanctioned options, review for anything new with an operating owner and upgrade story, and a default of "use what we run" unless the workload demonstrably doesn't fit. **Ch 24, 35, 43.**

??? question "B5 · What makes a technical strategy effective?"
    **Short answer:** An honest diagnosis, a direction tied to business outcomes, a few explicit bets and non-goals, paved roads that make it easy to follow, and progress people can see. **Ch 43.**

## Scenario prompts for B5 interviews

??? example "B5 scenario · Every release needs four services deployed in order"
    Expect: diagnosis of the coupling (shared schema, shared domain library, unversioned APIs, synchronous chains); a strategy that splits schemas with grants, replaces the shared model with platform starters and per-client DTOs, introduces additive versioning with consumer-driven contracts, moves non-critical work to events; progress measured with DORA and scorecards; leadership through RFCs, pilots and paved roads. **Ch 20, 28, 35, 41, 43.**

??? example "B5 scenario · The same class of outage happened three times this year"
    Expect: a theme review across incidents rather than three local fixes; identification of the systemic factor (for example synchronous calls without timeouts); platform changes (default timeouts in the client starter, CI checks, review checklist); verification by game day; and a note on why the previous reviews didn't find it. **Ch 26, 41, 43.**

??? example "B5 scenario · The board wants 'an AI strategy' in 90 days"
    Expect: identification of use cases where AI explains, drafts or routes with measurable value; an explicit list of where it won't be used; engineering prerequisites (evaluation, tool authorization, cost controls, fallbacks, data-flow review); a pilot with success metrics; and governance rather than a platform bet. **Ch 40, 43.**

??? example "B5 scenario · Cloud spend grew 60% while orders grew 20%"
    Expect: normalize to cost per order; find the top drivers by service; separate growth from waste (idle requests, cardinality, log volume, unbounded AI usage, over-provisioned dedicated tenants); fix with right-sizing, startup improvements enabling faster scale-down, caching and query fixes; institutionalize a monthly cost review. **Ch 27, 29, 30, 34, 38, 43.**

---

[:material-arrow-left: B4 · 8–12 years](b4-8-12-years.md) · [System Design :material-arrow-right:](system-design.md)
