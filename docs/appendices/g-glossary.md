# Appendix G · Glossary

Terms used throughout the handbook, with a short definition and the chapter where each is explained. Grocery-domain terms are included where they appear in examples.

## A

| Term | Definition | Ch |
|---|---|---|
| **Access matrix** | An executable table of role × endpoint × expected status, used as the authorization test suite | 17, 39 |
| **ACID** | Atomicity, consistency, isolation, durability — properties of a database transaction | 16 |
| **ADR** | Architecture Decision Record — a one-page record of a decision, its alternatives and consequences | 43 |
| **Aggregate** | A cluster of domain objects with one root that enforces invariants and forms the transaction boundary | 37 |
| **Alias (search)** | A name pointing at a concrete index, enabling zero-downtime reindexing | 22 |
| **Anticorruption layer (ACL)** | An adapter translating an external system's model into your own | 37 |
| **AOP** | Aspect-oriented programming — applying cross-cutting behaviour around method calls via proxies | 04 |
| **AOT (Spring)** | Ahead-of-time processing that generates bean definitions at build time | 29 |
| **AOT cache (JDK)** | JDK 24+ mechanism storing pre-loaded and linked classes to speed startup | 29 |
| **At-least-once** | Delivery guarantee where messages may be redelivered; requires idempotent consumers | 23 |
| **Audience (`aud`)** | JWT claim naming the intended recipient API; must be validated | 18 |
| **Auto-configuration** | Conditional configuration applied by Boot based on classpath and properties | 05, 41 |

## B

| Term | Definition | Ch |
|---|---|---|
| **Backpressure** | A consumer signalling how much it can handle, so producers don't overwhelm it | 31 |
| **Band (B1–B5)** | The handbook's experience levels, from 0–2 years to 12–15+ years | 00 |
| **BFF** | Backend for frontend — a composition service shaped for one client type | 32 |
| **Blind index** | A keyed hash of an encrypted value allowing equality lookup without decryption | 39 |
| **BOM** | Bill of materials — a dependency version catalogue | 01 |
| **Bounded context** | The scope within which a domain model and its language are consistent | 37 |
| **Breakpoint test** | A load test finding the maximum throughput per pod | 34 |
| **Bulkhead** | A limit on concurrent calls to one dependency, isolating failures | 26 |
| **Burn rate** | How fast an error budget is being consumed relative to the SLO | 27 |

## C

| Term | Definition | Ch |
|---|---|---|
| **Cache stampede** | Many concurrent misses on an expired hot key overwhelming the source | 21 |
| **Canary** | Releasing to a small share of traffic with automated analysis before full rollout | 30 |
| **Cardinality** | The number of distinct tag combinations (time series) of a metric | 27 |
| **CDC** | Change data capture — reading database changes from the log (e.g. Debezium) | 36 |
| **CDS** | Class Data Sharing — archived class metadata to speed JVM startup | 29 |
| **Cell** | An isolated copy of the stack serving a subset of tenants, limiting blast radius | 38 |
| **Choreography** | A saga style where services react to each other's events without a coordinator | 36 |
| **Circuit breaker** | Stops calling a failing dependency and fails fast until it recovers | 26 |
| **Client credentials** | OAuth2 grant for service-to-service authentication | 18 |
| **Compensation** | A semantic undo in a saga (refund, release stock) | 36 |
| **Config tree** | Configuration read from a directory of files, typically mounted secrets | 06 |
| **Consumer group** | Kafka consumers sharing partitions and offsets | 23 |
| **Context map** | The relationships between bounded contexts | 37 |
| **Coordinated omission** | A load-testing flaw where slow responses reduce the request rate, hiding latency | 34 |
| **CQRS** | Separating write and read models | 36 |

## D

| Term | Definition | Ch |
|---|---|---|
| **Data key / envelope encryption** | A per-value key encrypted by a KMS master key and stored with the ciphertext | 39 |
| **Deadline (gRPC)** | An absolute time limit propagated across a call chain | 32 |
| **Degradation** | Serving a worse but acceptable response when a dependency fails | 26 |
| **Delegate** | The handbook's layer between controller and service, mapping DTOs to use cases | 01, 08 |
| **Digest** | The content hash identifying an exact container image | 29 |
| **DLT / DLQ** | Dead-letter topic/queue for messages that can't be processed | 23, 24 |
| **DLX** | Dead-letter exchange in RabbitMQ | 24 |
| **Domain event** | A record of something that happened in the domain, in past tense | 37 |
| **DORA metrics** | Deployment frequency, lead time, change failure rate, time to restore | 43 |
| **DPDP Act** | India's Digital Personal Data Protection Act 2023 | 39 |
| **DSR** | Data subject request — access, correction or erasure of personal data | 39 |
| **Dual write** | Writing to two systems without atomicity, risking inconsistency | 36 |

## E–G

| Term | Definition | Ch |
|---|---|---|
| **Error budget** | The allowed failure within an SLO window | 27 |
| **ETag** | A version identifier for a resource used in conditional requests | 08 |
| **Exemplar** | A link from a metric bucket to an example trace | 27 |
| **Expand/contract** | Backward-compatible schema change in stages | 14 |
| **Failure analyzer** | Boot component turning a startup exception into actionable advice | 41 |
| **Fencing token** | A monotonically increasing token that makes stale lock holders detectable | 22 |
| **Flame graph** | Visualization of sampled stacks; width shows share of time | 34 |
| **Freeze window** | A period (e.g. Diwali) when risky changes aren't deployed | 30, 42 |
| **GMV** | Gross merchandise value — total value of orders | 27 |
| **Golden file** | A checked-in expected output (e.g. JSON) used to detect behaviour change | 11, 42 |
| **GSTIN** | Goods and Services Tax Identification Number (India) | 09 |

## H–K

| Term | Definition | Ch |
|---|---|---|
| **Hexagonal architecture** | Ports and adapters: a framework-free core with dependencies pointing inward | 37 |
| **HMAC** | Keyed hash used to verify webhook authenticity | 18 |
| **HPA** | Horizontal Pod Autoscaler | 30 |
| **HTTP interface** | A Java interface with `@HttpExchange` methods backed by a client | 19 |
| **Hub** | A dark store or fulfilment location serving a set of pincodes | 22, 24 |
| **Idempotency key** | A client-supplied key making retries of a non-idempotent request safe | 04 |
| **Inbox** | A table recording processed event ids so consumers deduplicate | 23, 36 |
| **Invariant** | A rule that must always hold for an aggregate | 37 |
| **JWKS** | JSON Web Key Set — the public keys used to verify JWT signatures | 18 |
| **KEDA** | Kubernetes Event-Driven Autoscaling — scales on lag, queue depth, schedules | 30 |
| **Keyset pagination** | Cursor pagination using the last seen sort key instead of offsets | 12, 20 |
| **KMS** | Key management service holding master keys | 39 |
| **KRaft** | Kafka's ZooKeeper-free consensus mode; the only mode in Kafka 4 | 23 |

## L–N

| Term | Definition | Ch |
|---|---|---|
| **Little's law** | Concurrency = throughput × latency | 34 |
| **Load shedding** | Rejecting low-priority work early when overloaded | 26 |
| **MDC** | Mapped Diagnostic Context — per-thread logging fields | 07 |
| **Modular monolith** | One deployable with enforced module boundaries | 37 |
| **mTLS** | Mutual TLS — both sides authenticate with certificates | 30, 39 |
| **N+1** | One query for a list plus one per item | 13 |
| **N-1 support** | Supporting the previous major version of a platform library | 41 |
| **Native image** | A GraalVM ahead-of-time compiled executable | 29 |

## O–P

| Term | Definition | Ch |
|---|---|---|
| **Observation API** | Micrometer API producing metrics and spans from one instrumentation point | 27 |
| **Open model** | Load testing by arrival rate, independent of response time | 34 |
| **OpenRewrite** | Automated, type-aware source code transformations | 42 |
| **Orchestration** | A saga style with a coordinator issuing commands and tracking state | 36 |
| **Outbox** | A table written in the business transaction, later published to a broker | 36 |
| **Partition (Kafka)** | An ordered shard of a topic; the unit of parallelism | 23 |
| **Passkey** | A WebAuthn credential replacing passwords | 18 |
| **PDB** | PodDisruptionBudget — limits voluntary disruptions | 30 |
| **Persisted query** | A GraphQL query registered in advance and referenced by hash | 32 |
| **Pincode** | India's six-digit postal code; the platform's serviceability key | 09 |
| **Pinning** | A virtual thread unable to unmount, blocking its carrier thread | 25 |
| **PKCE** | Proof Key for Code Exchange — protects authorization codes for public clients | 18 |
| **Platform starter** | An internal Boot starter carrying cross-cutting conventions | 41 |
| **Port** | An interface defined by the core, implemented by an adapter | 37 |
| **Prefetch** | Number of unacknowledged messages a RabbitMQ consumer may hold | 24 |
| **Problem details** | RFC 9457 standard error format | 10 |
| **Projection / read model** | A derived, rebuildable view built from events | 36 |
| **Provider state** | A precondition a provider sets up before replaying a contract | 28 |
| **Proxy** | A Spring-generated wrapper applying advice (transactions, caching, security) | 04 |

## Q–R

| Term | Definition | Ch |
|---|---|---|
| **Quorum queue** | RabbitMQ's Raft-replicated queue type | 24 |
| **RAG** | Retrieval-augmented generation — search plus prompting | 40 |
| **Readiness scorecard** | Per-service checklist of upgrade prerequisites | 42 |
| **Rebalance** | Reassignment of Kafka partitions among consumers | 23 |
| **Reconciliation** | Comparing systems to detect drift | 33, 36 |
| **Replication slot** | PostgreSQL mechanism retaining WAL for a logical consumer | 36 |
| **Retry budget** | A cap on retries as a fraction of traffic | 26 |
| **RLS** | Row-level security — database policies filtering rows | 38 |
| **RFC (internal)** | Request for Comments — a proposal document with a decision deadline | 43 |
| **Runbook** | Step-by-step operational instructions linked from an alert | 27, 43 |

## S

| Term | Definition | Ch |
|---|---|---|
| **Saga** | A sequence of local transactions with compensations | 36 |
| **SBOM** | Software bill of materials | 01, 29 |
| **Scoped value** | Java 25 immutable, scope-bound alternative to `ThreadLocal` | 25 |
| **Service catalog** | Machine-readable registry of services, owners, SLOs and dependencies | 35 |
| **ShedLock** | Library ensuring a scheduled job runs on one instance | 25 |
| **Shadow traffic** | Sending copies of requests to a new implementation for comparison | 35 |
| **Slice test** | A Spring test loading one layer (`@WebMvcTest`, `@DataJpaTest`) | 15 |
| **SKU** | Stock-keeping unit — a sellable product variant | throughout |
| **SLI / SLO** | Service level indicator / objective | 27 |
| **SSE** | Server-sent events — server-to-client streaming over HTTP | 31, 32 |
| **SSRF** | Server-side request forgery | 39 |
| **Stale-while-revalidate** | Serving a cached value while refreshing it in the background | 21 |
| **Static membership** | Kafka consumers with stable ids to avoid rebalances on restart | 23 |
| **STOMP** | Messaging protocol layered on WebSocket | 32 |
| **Strangler fig** | Incrementally replacing a system by routing functionality to new components | 35 |
| **STRIDE** | Threat categories: spoofing, tampering, repudiation, disclosure, DoS, elevation | 39 |
| **Sweeper** | A periodic job processing due items via a query | 25 |

## T–Z

| Term | Definition | Ch |
|---|---|---|
| **Tail sampling** | Deciding which traces to keep after seeing them complete | 27 |
| **TDS** | Tax deducted at source (India), part of seller settlement | 33 |
| **Tenant** | A customer organization sharing the platform with isolated data | 38 |
| **Timeout budget** | Allocation of a request's deadline across its dependencies | 19, 34 |
| **Tolerant reader** | A consumer ignoring unknown fields and values | 20, 23 |
| **Tool calling** | A model requesting that your code perform an operation | 40 |
| **Ubiquitous language** | Shared vocabulary between domain experts and engineers within a context | 37 |
| **Value object** | Immutable, identity-less domain object compared by value | 37 |
| **Virtual thread** | A JVM-managed lightweight thread that unmounts while blocked | 25 |
| **WAL** | PostgreSQL write-ahead log | 36 |
| **WireMock** | HTTP stub server used for dependency tests | 28 |

---

[:material-arrow-left: F Troubleshooting Playbook](f-troubleshooting-playbook.md) · [H Resources :material-arrow-right:](h-resources.md)
