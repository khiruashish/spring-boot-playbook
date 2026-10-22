# B3 · 5–8 Years

How things work internally, how they fail, and how to design within a service. A strong B3 candidate owns a service, explains mechanisms rather than recipes, and answers "what happens when it breaks?" without prompting.

## Container, lifecycle and proxies

??? question "B3 · Walk through the lifecycle of a Spring bean."
    **Short answer:** Definition registered → `BeanFactoryPostProcessor`s modify definitions → instantiation → property/constructor injection → `Aware` callbacks → `BeanPostProcessor` before-init → `@PostConstruct` / `afterPropertiesSet` → after-init (where proxies are created) → ready → on shutdown `@PreDestroy` / `destroy`. **Ch 03.**

??? question "B3 · Where exactly are AOP proxies created, and why does that matter?"
    **Short answer:** In `postProcessAfterInitialization` by an auto-proxy creator. Consequences: `@PostConstruct` runs on the target (no advice), self-calls bypass the proxy, and final classes or methods can't be proxied with CGLIB. **Ch 03, 04.**

??? question "B3 · JDK dynamic proxy vs CGLIB?"
    **Short answer:** JDK proxies implement interfaces; CGLIB subclasses the class. Boot defaults to CGLIB (proxy target class), which needs non-final classes and methods. **Ch 04.**

??? question "B3 · How does `SmartLifecycle` help with graceful shutdown?"
    **Short answer:** Components start and stop in phases; consumers and schedulers can stop before the web server and pools, so in-flight work drains in a controlled order. **Ch 03, 30.**

## Auto-configuration and configuration

??? question "B3 · How does Boot decide which auto-configurations apply?"
    **Short answer:** It reads the `AutoConfiguration.imports` files, filters by exclusions and fast class conditions, orders by before/after, and registers classes whose conditions pass — after user configuration, which is why `@ConditionalOnMissingBean` works. **Ch 05, 41.**

??? question "B3 · How do you debug a missing bean?"
    **Short answer:** `/actuator/conditions` or `--debug` — the condition evaluation report states exactly which condition didn't match and why. **Ch 41.**

??? question "B3 · What are the pitfalls of `@ConditionalOnBean`?"
    **Short answer:** It's evaluated against the registry as it's being built, so a bean defined later isn't seen. Use explicit ordering, or `ObjectProvider` for optional collaborators. **Ch 41.**

## Web and JSON internals

??? question "B3 · Trace a request through Spring MVC."
    **Short answer:** Filters (security, correlation) → `DispatcherServlet` → handler mapping → interceptors → argument resolvers and validation → controller → return-value handling and message conversion → exception resolvers (advice) on failure. **Ch 08, 10.**

??? question "B3 · Why don't exceptions thrown in filters reach `@ControllerAdvice`?"
    **Short answer:** Filters run before the `DispatcherServlet`; handle errors in the filter, or delegate to a `HandlerExceptionResolver`, to keep one error format. **Ch 10, 17.**

??? question "B3 · How do you prevent polymorphic deserialization vulnerabilities?"
    **Short answer:** Avoid default typing; use explicit subtypes with allow-lists; restrict trusted packages for Kafka/Redis serializers; prefer typed serializers per cache. **Ch 11, 21, 23.**

## Data and transactions

??? question "B3 · Explain the JPA persistence context and dirty checking."
    **Short answer:** Managed entities are tracked for the transaction; at flush, Hibernate compares state to snapshots and issues updates. Large contexts cost memory and flush time; clear or use projections for bulk reads. **Ch 13.**

??? question "B3 · Why is `open-in-view` dangerous?"
    **Short answer:** It keeps the session open during view rendering, enabling lazy loading outside the service layer — hidden queries, N+1 and connections held for the whole request. **Ch 13.**

??? question "B3 · Describe transaction propagation modes that matter in practice."
    **Short answer:** `REQUIRED` joins or creates; `REQUIRES_NEW` suspends and creates (two connections); `MANDATORY` requires an existing one (used for outbox writes); `NOT_SUPPORTED` suspends. **Ch 16, 36.**

??? question "B3 · What happens when an inner `REQUIRED` method throws and the outer catches it?"
    **Short answer:** The shared transaction is marked rollback-only; the outer commit then throws `UnexpectedRollbackException`. **Ch 16.**

??? question "B3 · Why must remote calls stay outside transactions?"
    **Short answer:** A slow call holds a database connection and locks for its whole duration, exhausting the pool; and a rollback can't undo the remote side effect. **Ch 16.**

??? question "B3 · How do you size a HikariCP pool?"
    **Short answer:** From concurrency (Little's law) and database capacity, usually small; watch `pending`. Multiply by pods and services to check against `max_connections`. **Ch 12, 34.**

??? question "B3 · How do you run a migration on a 40-million-row table without downtime?"
    **Short answer:** Expand/contract, `CREATE INDEX CONCURRENTLY`, batched backfills, avoiding long `ACCESS EXCLUSIVE` locks, and rehearsal on production-sized data with time and lock budgets. **Ch 14, 28.**

## Security internals

??? question "B3 · Describe the security filter chain flow."
    **Short answer:** Context loading, headers, CORS, CSRF, authentication filters, anonymous, `ExceptionTranslationFilter`, then `AuthorizationFilter`; denials become 401 via the entry point or 403 via the access-denied handler. **Ch 17.**

??? question "B3 · Walk through JWT validation."
    **Short answer:** Extract bearer token → decoder parses header → key by `kid` from cached JWKS → signature → validators (timestamps with skew, issuer, audience, custom) → converter to authorities. **Ch 18.**

??? question "B3 · How does key rotation avoid downtime?"
    **Short answer:** Publish old and new keys in the JWKS; sign with the new `kid`; decoders refresh on unknown `kid`; remove the old key only after the longest token lifetime. **Ch 18.**

??? question "B3 · How do you implement immediate revocation with JWTs?"
    **Short answer:** Short access-token lifetime plus a `jti` deny list checked by a validator, and refresh-token family revocation with reuse detection. **Ch 18.**

## Clients, caching, search

??? question "B3 · Connect, read and connection-request timeouts — what does each protect against?"
    **Short answer:** Connect: establishing TCP/TLS. Read: waiting for data. Connection-request: waiting for a pooled connection — pool exhaustion is invisible without it. **Ch 19.**

??? question "B3 · How does timeout budgeting work across a call chain?"
    **Short answer:** Each hop gets a share of the caller's remaining deadline, including retries; downstream timeouts must be shorter than upstream ones. **Ch 19, 34.**

??? question "B3 · When should cache eviction happen relative to the transaction?"
    **Short answer:** After commit — otherwise another thread repopulates the cache from pre-commit state. **Ch 21.**

??? question "B3 · How do you invalidate local caches across pods?"
    **Short answer:** Broadcast events (Kafka or Redis pub/sub) consumed by every pod, or versioned key prefixes; keep a short TTL as a safety net. **Ch 21.**

??? question "B3 · How do you reindex search without downtime?"
    **Short answer:** New index with the new mapping, bulk load from the source of truth plus catch-up, validate counts and golden queries, then an atomic alias swap. **Ch 22.**

??? question "B3 · What are the limits of a Redis distributed lock?"
    **Short answer:** It's an efficiency lock: GC pauses and failover can allow two holders. Use database constraints, conditional updates or fencing tokens for correctness. **Ch 22.**

## Messaging internals

??? question "B3 · Explain consumer-group rebalancing and how to make deploys smooth."
    **Short answer:** Membership changes reassign partitions; cooperative sticky assignment moves only what's needed, static membership lets a restarting pod reclaim its partitions, and idempotent processing makes any replay harmless. **Ch 23.**

??? question "B3 · What do Kafka transactions guarantee — and not?"
    **Short answer:** Atomic produce and offset commits within Kafka for read-process-write flows. They do not include your database; that requires the outbox. **Ch 23, 36.**

??? question "B3 · What happens if processing exceeds `max.poll.interval.ms`?"
    **Short answer:** The consumer is evicted, a rebalance occurs and uncommitted records are redelivered. Reduce batch size, speed up processing or pause explicitly. **Ch 23.**

??? question "B3 · How do you retry a RabbitMQ message after 30 seconds without blocking?"
    **Short answer:** Publish to a TTL queue without consumers whose dead-letter exchange routes back to the work exchange, with an attempt counter; park after N attempts. **Ch 24.**

## Concurrency, resilience, observability

??? question "B3 · What actually changes when you enable virtual threads?"
    **Short answer:** Request handling and executors create a virtual thread per task; blocking is cheap, so thread count stops limiting throughput and downstream resources become the bottleneck — bulkheads become essential. **Ch 25.**

??? question "B3 · What is pinning?"
    **Short answer:** A virtual thread that can't unmount blocks its carrier — historically `synchronized` around blocking I/O (fixed in JDK 24), still native frames. Detect with JFR or `jdk.tracePinnedThreads`. **Ch 25.**

??? question "B3 · Explain retry amplification."
    **Short answer:** Retries at several layers multiply load (3×3×3 = 27 requests per user action) when a dependency is already struggling. Use one retry layer, jitter, budgets and circuit breakers. **Ch 26.**

??? question "B3 · Should an open circuit breaker make the pod unready?"
    **Short answer:** No — every pod would drop out, and the degraded path the breaker enables would never serve traffic. Surface it in health details and alerts. **Ch 26, 30.**

??? question "B3 · What does the Observation API give you over plain metrics?"
    **Short answer:** One instrumentation point producing metrics and spans, with low-cardinality keys for tags and high-cardinality keys for span attributes. **Ch 27.**

??? question "B3 · Head vs tail sampling?"
    **Short answer:** Head sampling decides at the start and may drop the trace you need; tail sampling decides in the collector after seeing the whole trace, keeping errors and slow requests. **Ch 27.**

## Testing, packaging, Kubernetes, reactive

??? question "B3 · How does consumer-driven contract testing prevent breakage?"
    **Short answer:** Consumers publish pacts of their real expectations; providers verify them in CI; `can-i-deploy` blocks a release that would break a consumer in production. **Ch 28.**

??? question "B3 · How does CDS improve startup?"
    **Short answer:** A training run archives parsed class data that later starts map directly; it must match the JDK and classpath, so regenerate on every upgrade. **Ch 29.**

??? question "B3 · Walk through what happens when a pod is deleted."
    **Short answer:** Marked terminating and removed from endpoints (asynchronously) → preStop → SIGTERM → readiness refuses → requests drain → lifecycle phases stop → pools close → exit, or SIGKILL after the grace period. **Ch 30.**

??? question "B3 · Explain assembly time vs subscription time in Reactor."
    **Short answer:** Building the chain creates a blueprint; nothing runs until subscription, when demand flows upstream and signals downstream. Hence "nothing happened" bugs and confusing stack traces. **Ch 31.**

??? question "B3 · How do you choose a backpressure strategy?"
    **Short answer:** By data semantics: drop or keep-latest for live values, bounded buffer for bursts, `limitRate` for paged data — never unbounded buffering on infinite streams. **Ch 31.**

## Protocols, batch, performance

??? question "B3 · How do you fix N+1 in GraphQL?"
    **Short answer:** `@BatchMapping`/DataLoader to fetch all keys at a level in one call, plus a test asserting the downstream call count. **Ch 32.**

??? question "B3 · Why are gRPC deadlines better than per-hop timeouts?"
    **Short answer:** A deadline is absolute and propagated, so the whole chain gives up together and no work continues after the caller has. **Ch 32.**

??? question "B3 · What makes a batch job restartable?"
    **Short answer:** Stable identifying parameters, deterministic reader ordering, idempotent writes, and readers persisting position in the execution context — proven by a fail-then-restart test with exact counts. **Ch 33.**

??? question "B3 · Explain Little's law and how you use it."
    **Short answer:** Concurrency = throughput × latency. It sizes pools and bulkheads and explains why rising latency exhausts resources. **Ch 34.**

??? question "B3 · What is coordinated omission?"
    **Short answer:** Closed-model load tests stop sending requests while the system is slow, hiding queueing. Use an open (arrival-rate) model. **Ch 34.**

??? question "B3 · How do you find a memory leak?"
    **Short answer:** Watch heap after full GC over time; if the floor rises, take a heap dump and follow the dominator tree to GC roots — often an unbounded cache or uncleared ThreadLocal. **Ch 34.**

## Distributed data and architecture

??? question "B3 · Walk through an orchestrated saga's failure handling."
    **Short answer:** Persisted state with guarded transitions; step failures arrive as events and move to compensating; compensations run only for completed steps and are idempotent; a sweeper enforces deadlines; repeated failure goes to STUCK with an alert. **Ch 36.**

??? question "B3 · What are the operational risks of CDC with Debezium?"
    **Short answer:** A stalled replication slot retains WAL and can fill the disk; connector lag delays events; schema changes can break connectors. Alert on slot lag and set `max_slot_wal_keep_size`. **Ch 36.**

??? question "B3 · How do you decide aggregate boundaries?"
    **Short answer:** By invariants that must hold at the same instant; if seconds of eventual consistency are acceptable, use separate aggregates connected by events. **Ch 37.**

??? question "B3 · How does the Modulith event publication registry work?"
    **Short answer:** Publications are persisted in the business transaction and completed when listeners succeed; incomplete ones can be republished — an in-process outbox, making later extraction mechanical. **Ch 37.**

??? question "B3 · How do you prove tenant isolation?"
    **Short answer:** A reflective leak suite over every repository with two seeded tenants, plus tests for native queries (RLS), pooled-connection state, async and messaging paths — in every build. **Ch 38.**

??? question "B3 · How would you implement a data-erasure request across many services?"
    **Short answer:** Catalog-driven orchestration so nothing is missed; per-service erase and export; anonymize where retention is legally required and record the basis; verify no data remains; audit the whole request. **Ch 39.**

??? question "B3 · How do you evaluate an AI feature in CI?"
    **Short answer:** A golden set with property assertions, plus refusal, prompt-injection (in retrieved content) and authorization tests that also check the audit trail — run nightly and gating prompt or model changes. **Ch 40.**

??? question "B3 · How do you test auto-configuration honestly?"
    **Short answer:** `ApplicationContextRunner` with back-off tests for each bean and `FilteredClassLoader` to simulate missing optional libraries. **Ch 41.**

??? question "B3 · How do you test cross-version message compatibility during an upgrade?"
    **Short answer:** Deserialize real payloads captured from the old version with the new stack, and payloads from the new stack with an old-configured mapper — both directions, per topic. **Ch 42.**

## Leadership (B3 entry level)

??? question "B3 · How do you lead a SEV-1 incident?"
    **Short answer:** Assign roles (commander, comms, operations), restore first by rollback or degradation, keep a timeline, update on a cadence, then run a blameless review with owned actions. **Ch 43.**

??? question "B3 · What makes a good post-incident action?"
    **Short answer:** Specific, owned, dated, and changing a system — a test, alert or library default — rather than asking people to be more careful. **Ch 43.**

## More B3 questions

### Container and configuration internals

??? question "B3 · What's the difference between a `BeanFactoryPostProcessor` and a `BeanPostProcessor`?"
    **Short answer:** The former modifies bean definitions before instantiation (placeholders, scopes); the latter modifies or wraps bean instances around initialization (proxies, injection). **Ch 03.**

??? question "B3 · Why must `BeanFactoryPostProcessor` `@Bean` methods be static?"
    **Short answer:** They run before regular beans exist; a non-static method forces early instantiation of the enclosing configuration and can break processing. **Ch 03.**

??? question "B3 · How are circular dependencies handled, and why are they a smell?"
    **Short answer:** Constructor cycles fail at startup (and Boot disallows field-injection cycles by default); cycles usually indicate a missing abstraction or misplaced responsibility. **Ch 02.**

??? question "B3 · What does `proxyBeanMethods = false` change?"
    **Short answer:** No CGLIB subclass for the configuration, so calling one `@Bean` method from another creates a new instance instead of returning the singleton — faster startup, but inject dependencies as parameters. **Ch 02.**

??? question "B3 · How does relaxed binding work?"
    **Short answer:** Properties bind from kebab, camel, underscore and environment-variable forms to the same `@ConfigurationProperties` field. **Ch 06.**

??? question "B3 · How does an `EnvironmentPostProcessor` differ from `@PropertySource`?"
    **Short answer:** It runs very early, before the context, and can add or reorder property sources with explicit precedence; `@PropertySource` is processed later and has limited precedence control. **Ch 06, 41.**

### Web and error handling internals

??? question "B3 · How do argument resolvers work, and when would you write one?"
    **Short answer:** `HandlerMethodArgumentResolver`s build controller parameters from the request; write one for cross-cutting context such as the current customer or tenant. **Ch 08.**

??? question "B3 · How does content negotiation pick a converter?"
    **Short answer:** From the `Accept` header and `produces` attributes against registered `HttpMessageConverter`s; mismatches yield 406. **Ch 08.**

??? question "B3 · How do you keep one error format for filter and controller exceptions?"
    **Short answer:** Filters catch and delegate to the `HandlerExceptionResolver`, and security uses custom entry points and access-denied handlers writing problem bodies. **Ch 10, 17.**

??? question "B3 · How does method validation work internally?"
    **Short answer:** A `MethodValidationPostProcessor` adds an AOP interceptor for `@Validated` beans; proxy rules therefore apply. **Ch 09.**

### Data internals

??? question "B3 · When does Hibernate flush?"
    **Short answer:** Before commit, before queries that may be affected (auto flush), and on explicit `flush()`. Unexpected flushes cause surprising SQL timing and constraint errors. **Ch 13.**

??? question "B3 · Why does pagination with a collection fetch join misbehave?"
    **Short answer:** Hibernate can't paginate rows of a join in SQL, so it paginates in memory; enable the fail-fast setting and use two queries (ids, then fetch). **Ch 13.**

??? question "B3 · How do isolation levels affect the platform?"
    **Short answer:** PostgreSQL defaults to read committed; lost updates are prevented by optimistic locking or conditional updates rather than raising isolation globally. **Ch 16.**

??? question "B3 · How do you detect long-running transactions in production?"
    **Short answer:** `pg_stat_activity` for idle-in-transaction sessions, Hikari active-connection durations, and a transaction timeout. **Ch 12, 16.**

??? question "B3 · What does `SKIP LOCKED` enable?"
    **Short answer:** Multiple workers claiming different rows from the same queue table without blocking — the basis of relays, sweepers and job tables. **Ch 12, 25, 36.**

??? question "B3 · How do you keep migrations backward compatible during rolling deploys?"
    **Short answer:** Old code must work against the new schema: add before use, dual-write, switch reads, remove last — never drop or rename in the same release. **Ch 14.**

### Security internals

??? question "B3 · How does method security evaluate `@PreAuthorize`?"
    **Short answer:** An authorization interceptor evaluates the expression (or a bean method) against the current authentication before invoking the method; denials throw `AccessDeniedException`. **Ch 17.**

??? question "B3 · What is refresh-token reuse detection?"
    **Short answer:** Rotated refresh tokens are single-use; if a used token reappears, the whole family is revoked because one copy was stolen. **Ch 18.**

??? question "B3 · Why must webhook verification use raw bytes?"
    **Short answer:** Parsing and re-serializing changes the bytes (whitespace, ordering, number formats), so the HMAC no longer matches — or worse, matches different content. **Ch 18.**

??? question "B3 · How does a security context get lost, and how do you find out?"
    **Short answer:** Thread hops without propagation (async, executors, reactive schedulers); symptoms are `anonymousUser` in audits or unexpected 401/403 inside background work. **Ch 17, 25.**

### Clients, caching, search

??? question "B3 · How does `@Cacheable(sync = true)` work and what are its limits?"
    **Short answer:** It uses the cache's `get(key, loader)` so one thread computes per key per JVM; it can't be combined with `unless` and doesn't coordinate across pods. **Ch 21.**

??? question "B3 · How do typed Redis serializers reduce risk?"
    **Short answer:** No type information in payloads, so a poisoned entry can't instantiate arbitrary classes, and DTO changes fail predictably. **Ch 21.**

??? question "B3 · How do you implement stale-while-revalidate?"
    **Short answer:** Store a value with a freshness timestamp and a longer hard TTL; serve stale values immediately and refresh asynchronously. **Ch 21.**

??? question "B3 · Why put synonyms in the search analyzer only?"
    **Short answer:** Search-time synonyms can change without reindexing; index-time synonyms are faster but require a reindex for every change. **Ch 22.**

??? question "B3 · How do Lua scripts provide atomicity in Redis?"
    **Short answer:** The server executes the script without interleaving other commands; pass keys via `KEYS` for cluster slot routing. **Ch 22.**

### Messaging

??? question "B3 · How does `ErrorHandlingDeserializer` prevent poison-pill loops?"
    **Short answer:** It catches deserialization failures and hands the container a failed record with headers, so the error handler can route it to the DLT instead of failing the poll forever. **Ch 23.**

??? question "B3 · How do you replay dead letters safely?"
    **Short answer:** Seek by time, filter, republish to the original topic with audit, and only after consumers are idempotent and the root cause is fixed. **Ch 23.**

??? question "B3 · What does static membership change during rolling deploys?"
    **Short answer:** A consumer with a stable `group.instance.id` can restart within the session timeout without triggering a rebalance, keeping its partitions. **Ch 23.**

??? question "B3 · Why are publisher confirms asynchronous, and how do you use them with an outbox?"
    **Short answer:** The broker acknowledges later; mark outbox rows sent only in the confirm callback, correlated by id. **Ch 24.**

??? question "B3 · How does Pulsar's `Key_Shared` differ from Kafka partitions?"
    **Short answer:** It preserves per-key ordering while distributing keys across consumers dynamically, without a fixed partition count. **Ch 24.**

### Concurrency, resilience, observability

??? question "B3 · How does `ThreadPoolTaskExecutor` decide when to create threads?"
    **Short answer:** Up to core size, then queue; only when the queue is full does it grow to max size; beyond that the rejection policy runs. **Ch 25.**

??? question "B3 · Why never pool virtual threads?"
    **Short answer:** Pools amortize expensive creation; virtual threads are cheap. Pooling reintroduces a limit in the wrong place — use semaphores for concurrency limits. **Ch 25.**

??? question "B3 · What is a retry budget?"
    **Short answer:** A cap on retries as a fraction of successful traffic (e.g. 10%), so retries stop when a dependency is struggling. **Ch 26.**

??? question "B3 · How do you choose circuit-breaker thresholds?"
    **Short answer:** From measured latency and error distributions: slow-call threshold above normal p99, time-based windows, minimum calls suited to traffic, business errors ignored. **Ch 26.**

??? question "B3 · How do multi-window burn-rate alerts work?"
    **Short answer:** Page only when both a short and a long window exceed a burn-rate threshold, catching real outages quickly while ignoring brief blips. **Ch 27.**

??? question "B3 · How do you guard metric cardinality automatically?"
    **Short answer:** `MeterFilter.maximumAllowableTags` on risky meters, URI templates asserted in tests, and allow-lists for tag values. **Ch 27.**

### Testing, packaging, Kubernetes

??? question "B3 · Why does a Spring test suite create many contexts, and how do you fix it?"
    **Short answer:** Each distinct configuration (mock beans, properties, profiles) is a new cache key; standardize with composed test annotations and shared configuration. **Ch 15.**

??? question "B3 · How do you test `@ConditionalOnClass` branches?"
    **Short answer:** `ApplicationContextRunner` with `FilteredClassLoader` to hide the class. **Ch 41.**

??? question "B3 · How do you size JVM memory for a container?"
    **Short answer:** Set a memory limit and `MaxRAMPercentage` around 70–75%, then measure RSS: metaspace, thread stacks and direct buffers live outside the heap. **Ch 29.**

??? question "B3 · How does a config change reach running pods safely?"
    **Short answer:** Via a rollout triggered by a config-hash annotation, not runtime reloading, so every pod runs the same reviewed configuration. **Ch 06, 30.**

??? question "B3 · Why must NetworkPolicies allow DNS?"
    **Short answer:** Service discovery resolves through kube-dns; blocking UDP 53 breaks every outbound call. **Ch 30.**

### Architecture, tenancy, platform

??? question "B3 · How do domain events differ from integration events?"
    **Short answer:** Domain events describe changes inside a context, often in-process; integration events are published contracts for other services, versioned and evolved carefully. **Ch 23, 37.**

??? question "B3 · Why can't Hibernate `@TenantId` alone guarantee isolation?"
    **Short answer:** Native queries, JDBC access and bulk operations bypass it; database RLS provides the second layer. **Ch 38.**

??? question "B3 · How does an idempotent receiver work in Spring Integration?"
    **Short answer:** A `MetadataStore` records processed message keys and discards repeats — the integration-flow equivalent of an inbox. **Ch 33.**

??? question "B3 · How do you make AI tool output safe to use?"
    **Short answer:** Structured output validated against domain constraints, session-scoped tools, and human review for anything consequential. **Ch 40.**

---

[:material-arrow-left: B2 · 2–5 years](b2-2-5-years.md) · [B4 · 8–12 years :material-arrow-right:](b4-8-12-years.md)
