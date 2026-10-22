# Rapid Fire

One-line answers for last-minute revision. Cover the right column, read the left, answer aloud. Use as a warm-up or calibration tool — never as a pass/fail interview filter.

## Core and Boot

| Question | Answer |
|---|---|
| Default bean scope? | Singleton |
| Preferred injection style? | Constructor |
| Where are AOP proxies created? | `BeanPostProcessor` after initialization |
| Why doesn't `@Transactional` work on self-calls? | The call bypasses the proxy |
| Boot's default proxy type? | CGLIB (class-based) |
| File that registers auto-configurations? | `META-INF/spring/…AutoConfiguration.imports` |
| How does a user bean override auto-config? | `@ConditionalOnMissingBean` backs off |
| See why a bean is missing? | `/actuator/conditions` or `--debug` |
| Event listener that runs after commit? | `@TransactionalEventListener` |
| Ordered shutdown of components? | `SmartLifecycle` phases |

## Configuration and logging

| Question | Answer |
|---|---|
| Typed configuration? | `@ConfigurationProperties` + `@Validated` |
| Secrets as files? | Config tree via `spring.config.import=configtree:` |
| Renamed properties during an upgrade? | `spring-boot-properties-migrator` |
| Effective property sources? | `/actuator/env` |
| Change log level at runtime? | POST `/actuator/loggers/{name}` |
| Correlation id in logs? | MDC set in a filter, cleared in `finally` |
| Cheap disabled log statements? | Parameterized messages `{}` |

## Web and JSON

| Question | Answer |
|---|---|
| Status for create? | 201 + `Location` |
| Standard error body? | RFC 9457 `ProblemDetail` |
| Prevent lost updates? | ETag + `If-Match` → 412 |
| Idempotent POST? | `Idempotency-Key` with stored result |
| Money in JSON? | Decimal string |
| Dates in JSON? | ISO-8601 with offset |
| Why DTOs, not entities? | Decouple API from schema; avoid lazy-loading leaks |
| Built-in API versioning arrives in? | Framework 7 / Boot 4 |
| Deprecation headers? | `Deprecation`, `Sunset`, `Link` |
| Deep pagination? | Keyset/cursor, not offset |

## Data and transactions

| Question | Answer |
|---|---|
| N+1 fix? | Fetch join, `@EntityGraph`, projections + query-count test |
| Default rollback rule? | Unchecked exceptions only |
| `REQUIRES_NEW` cost? | A second connection while the first is suspended |
| Propagation for outbox writes? | `MANDATORY` |
| Inner `REQUIRED` throws, outer catches? | `UnexpectedRollbackException` at commit |
| Remote calls inside transactions? | Never — hold connections, can't roll back |
| `open-in-view` in production? | Disable it |
| Online index creation in PostgreSQL? | `CREATE INDEX CONCURRENTLY` |
| Schema changes without downtime? | Expand/contract |
| Work-queue locking? | `FOR UPDATE SKIP LOCKED` |

## Security

| Question | Answer |
|---|---|
| 401 vs 403? | Unauthenticated vs forbidden |
| Password storage? | BCrypt/Argon2 via `DelegatingPasswordEncoder` |
| CSRF needed for bearer-token APIs? | No |
| Is a JWT encrypted? | No — signed |
| The JWT claim teams forget to validate? | Audience |
| Immediate JWT revocation? | Short lifetime + `jti` deny list |
| Service-to-service auth? | Client credentials |
| Webhook verification? | HMAC over raw bytes, constant-time compare |
| SSRF defence? | Allow-list + resolve-then-check address |
| Card data storage? | Don't — tokenize |
| Tenant source of truth? | Token claim |
| RLS on owner role? | `FORCE ROW LEVEL SECURITY` |

## Clients, caching, NoSQL

| Question | Answer |
|---|---|
| Default synchronous client? | `RestClient` |
| Feign replacement? | HTTP interfaces (`@HttpExchange`) |
| Three timeouts? | Connect, read, connection-request |
| Retry which calls? | Idempotent + transient failures only |
| Cache stampede fixes? | `sync`, jitter, refresh-ahead, stale-while-revalidate |
| Evict cache when? | After commit |
| Cache failure behaviour? | Fail open via `CacheErrorHandler` |
| Redis structure for leaderboards? | Sorted set |
| Atomic multi-step Redis? | Lua script |
| Redis lock for correctness? | No — efficiency only |
| Zero-downtime reindex? | New index + alias swap |

## Messaging and async

| Question | Answer |
|---|---|
| Kafka delivery guarantee? | At-least-once |
| Ordering scope in Kafka? | Per partition (key) |
| Poison pill handling? | `ErrorHandlingDeserializer` + DLT |
| Idempotent consumer? | Inbox table or conditional update |
| Smooth rebalances? | Cooperative sticky + static membership |
| Kafka transactions cover your DB? | No — use the outbox |
| RabbitMQ HA queue type? | Quorum |
| RabbitMQ delayed retry? | TTL queue + DLX |
| Unroutable messages silently dropped unless? | `mandatory` + returns |
| Default executor danger? | Unbounded queue |
| Default scheduler pool size? | 1 |
| One job across pods? | ShedLock or CronJob |
| Pool virtual threads? | Never |
| Limit virtual-thread concurrency? | Semaphore bulkhead |

## Resilience and observability

| Question | Answer |
|---|---|
| Foundation of resilience? | Timeouts |
| Should business errors open breakers? | No |
| Retry vs breaker order? | Retry wraps breaker |
| Retry layers allowed? | One |
| Open breaker → unready? | No |
| Low-priority traffic under overload? | Shed with 503 + `Retry-After` |
| Metric tags with ids? | Never — cardinality |
| Alert on? | SLO burn rate and business metrics |
| Sampling that keeps errors? | Tail sampling in the collector |
| Gauge shows NaN? | Object garbage collected — hold a strong reference |
| Metrics + traces from one API? | Observation API |

## Testing, packaging, Kubernetes

| Question | Answer |
|---|---|
| `@MockBean` replacement? | `@MockitoBean` |
| Real DB in tests? | Testcontainers + `@ServiceConnection` |
| Test timeouts against a stub? | WireMock fixed delay / Toxiproxy |
| Block breaking provider releases? | Pact `can-i-deploy` |
| Adopt ArchUnit on legacy code? | `FreezingArchRule` |
| Layer extraction command? | `java -Djarmode=tools -jar app.jar extract --layers` |
| JVM heap in containers? | `MaxRAMPercentage` + memory limit |
| Deploy by? | Digest |
| Faster JVM startup? | CDS / JDK AOT cache |
| Liveness checks dependencies? | Never |
| Avoid dropped requests on shutdown? | `preStop` sleep + grace > drain |
| Capacity-preserving rollout? | `maxUnavailable: 0` |
| Maintenance protection? | PodDisruptionBudget |
| Scale consumers on? | Lag (KEDA), max = partitions |

## Reactive, protocols, batch, performance

| Question | Answer |
|---|---|
| Nothing runs until? | Subscription |
| Blocking call in WebFlux? | `boundedElastic`, detect with BlockHound |
| Live feed backpressure? | Drop or latest + sample |
| Reactive replacement for ThreadLocal? | Reactor Context |
| GraphQL N+1 fix? | `@BatchMapping` |
| gRPC advantage over HTTP timeouts? | Propagated deadlines |
| Removed proto field numbers? | `reserved` |
| Scale WebSocket across pods? | STOMP broker relay |
| Push-only protocol? | SSE |
| Batch restart requires? | Stable params, ordered reader, idempotent writes |
| Batch in Kubernetes? | CronJob, `Forbid`, real exit code |
| Little's law? | Concurrency = throughput × latency |
| Load test model? | Open (arrival rate) |
| CPU idle, latency high — profile how? | Wall-clock |
| Target peak utilization? | 60–70% |

## Architecture, platform, AI, leadership

| Question | Answer |
|---|---|
| Shared DB between services? | No — one writer per dataset |
| Display vs decide? | Display from projections, decide from the owner |
| Dual-write fix? | Outbox |
| Effectively once? | At-least-once + idempotency |
| Long cross-service flow? | Orchestrated saga with deadlines |
| Drift detection? | Reconciliation both directions |
| Aggregate rule? | One per transaction, reference by id |
| Domain imports Spring? | No — enforce with ArchUnit |
| Boundaries in a monolith? | Spring Modulith `verify()` |
| Kubernetes discovery? | Service DNS |
| Starter artifacts? | Autoconfigure (code) + starter (deps) |
| Test missing optional classes? | `FilteredClassLoader` |
| LLM decides prices or refunds? | Never |
| AI tool identity from? | The session, not the model |
| Empty retrieval → ? | Human handoff |
| Upgrade first? | Fix deprecations on current version |
| Upgrade order? | Platform libs → pilot → waves → core |
| Decision record? | ADR with revisit trigger |
| DORA measures? | The system, never individuals |
| Post-incident reviews are? | Blameless, with owned actions |

---

[:material-arrow-left: System Design](system-design.md) · [B Coding Exercises :material-arrow-right:](../b-coding-exercises.md)
