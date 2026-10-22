# B2 · 2–5 Years

Correct use under normal conditions, and the common pitfalls. A strong B2 candidate owns features end to end and can explain why the obvious approach sometimes fails.

## Spring core and AOP

??? question "B2 · Why doesn't `@Transactional` (or `@Cacheable`, `@Async`) work on self-invocation?"
    **Short answer:** These are implemented by proxies. A call from one method to another in the same class goes through `this`, not the proxy, so the advice never runs. Move the method to another bean or restructure. **Ch 04.**

??? question "B2 · How do you resolve two beans of the same type?"
    **Short answer:** `@Primary` for a default, `@Qualifier` at the injection point, or inject a `List`/`Map` of all candidates. **Ch 02.**

??? question "B2 · What's the risk of injecting a prototype bean into a singleton?"
    **Short answer:** It's injected once, so the singleton always holds the same instance. Use `ObjectProvider` or method injection to get a new one each time. **Ch 02.**

??? question "B2 · Application events vs direct calls — when to use events?"
    **Short answer:** When the publisher shouldn't know its listeners (loose coupling within a service). Use `@TransactionalEventListener` when the reaction must happen only after commit. **Ch 03.**

??? question "B2 · What's the difference between `@EventListener` and `@TransactionalEventListener`?"
    **Short answer:** `@EventListener` runs immediately inside the publisher's transaction; `@TransactionalEventListener` runs at a transaction phase (default after commit), so it never reacts to rolled-back work. **Ch 03, 16.**

## Configuration

??? question "B2 · Explain property source precedence."
    **Short answer:** Command-line args and environment variables override profile-specific files, which override `application.yml`; imported config trees fit in according to import order. `/actuator/env` shows the effective result. **Ch 06.**

??? question "B2 · How do you validate configuration at startup?"
    **Short answer:** `@ConfigurationProperties` with `@Validated` and Jakarta constraints — invalid config fails the app with a message naming the property. **Ch 06.**

??? question "B2 · How do you change a log level at runtime?"
    **Short answer:** POST to `/actuator/loggers/{name}` (secured, on the management port). **Ch 07, 27.**

??? question "B2 · How do you get a correlation id into every log line?"
    **Short answer:** A filter sets it in the MDC per request (and clears it); the log pattern or JSON encoder includes it; tracing adds `traceId`/`spanId` automatically. **Ch 07.**

## Web, validation, errors, JSON

??? question "B2 · How do you centralize error handling?"
    **Short answer:** A `@RestControllerAdvice` mapping exceptions to `ProblemDetail` with stable error codes, plus handling for validation errors — one error contract for all endpoints. **Ch 10.**

??? question "B2 · How do you write a custom validation constraint?"
    **Short answer:** An annotation with `@Constraint(validatedBy = …)` and a `ConstraintValidator` implementation, e.g. `@Pincode` or `@Gstin`. **Ch 09.**

??? question "B2 · What are validation groups for?"
    **Short answer:** Applying different constraint sets in different contexts (create vs update) via `@Validated(Create.class)`. **Ch 09.**

??? question "B2 · How do ETags prevent lost updates?"
    **Short answer:** The client sends `If-Match` with the version it read; the server rejects the write with 412 if the resource changed since. **Ch 08, 16.**

??? question "B2 · How do you make a POST idempotent?"
    **Short answer:** Require an `Idempotency-Key`; store the key with the result; on replay, return the stored result instead of re-executing. **Ch 04.**

??? question "B2 · How should money and dates be serialized in JSON?"
    **Short answer:** Money as decimal strings (or integer paise at gateways); dates as ISO-8601 with offsets. Verify with golden-file tests. **Ch 11.**

??? question "B2 · Why keep enums "open" in API contracts?"
    **Short answer:** So adding a value doesn't break older clients — they must tolerate unknown values rather than fail deserialization. **Ch 11, 20.**

## Data and transactions

??? question "B2 · How do you fix an N+1 query?"
    **Short answer:** Fetch joins, `@EntityGraph`, batch fetching, or a DTO projection — and add a query-count test so it doesn't return. **Ch 13.**

??? question "B2 · `JpaRepository`, `JdbcClient` or Spring Data JDBC — how do you choose?"
    **Short answer:** JPA for rich aggregates with change tracking; JDBC for simple, performance-critical or reporting queries; Spring Data JDBC for aggregate-oriented persistence without JPA's complexity. **Ch 12, 13.**

??? question "B2 · How should you paginate a large table?"
    **Short answer:** Offset pagination for small, shallow lists; keyset (cursor) pagination for deep or large lists, avoiding expensive offsets and counts. **Ch 12, 20.**

??? question "B2 · Why doesn't a checked exception roll back a transaction?"
    **Short answer:** By default only unchecked exceptions and errors trigger rollback; use `rollbackFor` for checked ones. **Ch 16.**

??? question "B2 · What does `REQUIRES_NEW` do, and when is it useful?"
    **Short answer:** Suspends the current transaction and starts a new one — useful for audit records that must persist even if the outer work rolls back. It holds two connections at once. **Ch 16.**

??? question "B2 · Optimistic vs pessimistic locking?"
    **Short answer:** Optimistic uses a version column and fails on conflict (good for low contention); pessimistic locks rows up front (`SELECT … FOR UPDATE`) for high-contention critical sections. **Ch 16.**

??? question "B2 · What's the expand/contract pattern?"
    **Short answer:** Make schema changes backward compatible in steps — add new structure, migrate and dual-write, switch reads, then remove the old — so old and new code both work during deploys. **Ch 14.**

## Security and tokens

??? question "B2 · How do you define multiple security configurations?"
    **Short answer:** Several `SecurityFilterChain` beans with `securityMatcher` and `@Order`; the first matching chain handles the request. **Ch 17.**

??? question "B2 · When is CSRF protection needed?"
    **Short answer:** When browsers send credentials automatically (cookies, Basic auth). Not for APIs authenticated by an `Authorization` header. **Ch 17.**

??? question "B2 · How do you enforce resource ownership?"
    **Short answer:** Scope queries by owner (returning 404), or use an `AuthorizationManager`/method security, and test with a second user. **Ch 17.**

??? question "B2 · Why validate the JWT audience claim?"
    **Short answer:** Otherwise a valid token issued for another API of the same issuer is accepted — a privilege escalation. **Ch 18.**

??? question "B2 · How does a service authenticate to another service?"
    **Short answer:** OAuth2 client credentials: a client id/secret obtains a scoped token that's cached and attached to outbound calls. **Ch 18, 19.**

??? question "B2 · How do you verify a webhook?"
    **Short answer:** HMAC over the raw body with the shared secret, constant-time comparison, deduplication by event id, then asynchronous processing. **Ch 18.**

## Clients, APIs and caching

??? question "B2 · What is an HTTP interface and why prefer it to Feign?"
    **Short answer:** An `@HttpExchange` Java interface backed by `RestClient`/`WebClient` — part of Spring Framework, sharing configuration and observability. Feign is in maintenance. **Ch 19.**

??? question "B2 · How do you translate downstream errors?"
    **Short answer:** A status handler at the client boundary mapping responses to domain or dependency exceptions — never forwarding raw downstream bodies. **Ch 19, 10.**

??? question "B2 · How do you deprecate an API version?"
    **Short answer:** `Deprecation`, `Sunset` and `Link` headers, usage telemetry per client, targeted outreach, brownouts, then `410 Gone`. **Ch 20.**

??? question "B2 · How do you choose cache TTLs?"
    **Short answer:** From the business staleness budget, with jitter to avoid synchronized expiry, and shorter TTLs where invalidation could be missed. **Ch 21.**

??? question "B2 · What is a cache stampede and how do you prevent it?"
    **Short answer:** Many concurrent misses on an expired hot key hitting the source. Prevent with `sync=true`/locking, jittered TTLs, refresh-ahead or stale-while-revalidate. **Ch 21.**

??? question "B2 · Why must cache keys include every dimension?"
    **Short answer:** A key missing the customer, tenant or pincode serves one user's data to another — a correctness and security bug. **Ch 21, 38.**

## NoSQL, messaging, async

??? question "B2 · Which Redis structure for a leaderboard, a lock, a queue?"
    **Short answer:** Sorted set for leaderboards; `SET NX PX` with a token for locks; list or Streams for queues. **Ch 22.**

??? question "B2 · Filter vs query in a search request?"
    **Short answer:** Filters are boolean, cached and don't score (price, category, availability); queries compute relevance (text). **Ch 22.**

??? question "B2 · How do you handle a poison message in Kafka?"
    **Short answer:** `ErrorHandlingDeserializer`, classify non-retryable exceptions, and send them to a dead-letter topic instead of blocking the partition. **Ch 23.**

??? question "B2 · How do you make a Kafka consumer idempotent?"
    **Short answer:** An inbox table keyed by `(consumer, eventId)` written in the same transaction as the side effect, or conditional updates/upserts. **Ch 23.**

??? question "B2 · Blocking retries vs retry topics?"
    **Short answer:** Blocking retries preserve order but stall the partition; retry topics keep the partition moving but lose ordering — use them for commutative work. **Ch 23.**

??? question "B2 · Why is `default-requeue-rejected: false` important in RabbitMQ?"
    **Short answer:** Otherwise a failing message is requeued and redelivered in a tight loop — the classic poison-message incident. **Ch 24.**

??? question "B2 · What's wrong with the default task executor configuration?"
    **Short answer:** Its queue is effectively unbounded, so `max-size` is never reached and tasks accumulate until memory runs out. Bound the queue and set a rejection policy. **Ch 25.**

??? question "B2 · How do you stop a scheduled job running on every pod?"
    **Short answer:** ShedLock (a lock row), a Kubernetes CronJob, or leader election — and keep the job idempotent anyway. **Ch 25.**

## Resilience and observability

??? question "B2 · Why must the retry wrap the circuit breaker?"
    **Short answer:** So each attempt passes through the breaker and retries fail fast once it's open; reversed, retries keep hammering a dead dependency. **Ch 26.**

??? question "B2 · Why shouldn't business exceptions open a circuit breaker?"
    **Short answer:** They mean the dependency works; counting them (e.g. payment declines) opens the breaker on legitimate traffic. **Ch 26.**

??? question "B2 · What is a bulkhead?"
    **Short answer:** A cap on concurrent calls to one dependency, so it can't consume all threads or connections. Essential with virtual threads. **Ch 25, 26.**

??? question "B2 · Why must metric tags have low cardinality?"
    **Short answer:** Each distinct tag combination is a new time series; ids as tags explode storage and cost. High-cardinality data belongs in traces and logs. **Ch 27.**

??? question "B2 · How do metrics, traces and logs work together?"
    **Short answer:** Metrics detect and alert, traces show which hop is slow, logs explain the specific case — joined by `traceId`. **Ch 27.**

## Testing, packaging, Kubernetes

??? question "B2 · How do you keep a Spring test suite fast?"
    **Short answer:** Share contexts (consistent configuration), share containers, prefer slices and unit tests, avoid `@DirtiesContext`, run classes in parallel with unique data. **Ch 15, 28.**

??? question "B2 · How do you test an HTTP client's timeout?"
    **Short answer:** WireMock with a fixed delay (or Toxiproxy), asserting both the error mapping and that the call returned within budget. **Ch 28.**

??? question "B2 · Why layer a Docker image?"
    **Short answer:** Dependencies change rarely and your code often; separate layers mean a code change ships megabytes, not the whole JAR. **Ch 29.**

??? question "B2 · Why deploy by digest instead of tag?"
    **Short answer:** Tags are mutable; a digest identifies exact content, making promotion and rollback unambiguous. **Ch 29.**

??? question "B2 · Why is a `preStop` sleep recommended?"
    **Short answer:** Endpoint removal propagates asynchronously; a brief pause prevents traffic arriving after SIGTERM. **Ch 30.**

## Architecture and platform

??? question "B2 · Why shouldn't microservices share a database?"
    **Short answer:** It couples schemas and releases, defeating independent deployment. One writer per dataset; others get copies via events. **Ch 35, 36.**

??? question "B2 · What is the outbox pattern?"
    **Short answer:** Write the event into a table in the same transaction as the business change; a relay publishes it. Atomic, at-least-once, nothing lost. **Ch 36.**

??? question "B2 · What is an aggregate?"
    **Short answer:** A cluster of objects with one root that enforces invariants and is the transaction boundary; other aggregates are referenced by id. **Ch 37.**

??? question "B2 · Why must tools in an AI assistant derive identity from the session?"
    **Short answer:** Tool arguments come from model output influenced by user input; a user id parameter lets a manipulated model access other users' data. **Ch 40.**

??? question "B2 · Why is `@ConditionalOnMissingBean` important in a starter?"
    **Short answer:** It lets applications override the starter's bean; without it they must exclude the whole auto-configuration. **Ch 41.**

??? question "B2 · How do you prepare for a major Spring Boot upgrade?"
    **Short answer:** Fix deprecations on the current version, upgrade to its latest minor, then use OpenRewrite and the properties migrator — and verify behaviour with golden files and contract tests. **Ch 42.**

## More B2 questions

### Core, Boot and configuration

??? question "B2 · How do you run code once the application is ready to serve?"
    **Short answer:** An `ApplicationRunner`/`CommandLineRunner` (runs before readiness flips, good for warm-up) or an `ApplicationReadyEvent` listener (after readiness). Choose by whether traffic should wait for it. **Ch 03.**

??? question "B2 · What is `ObjectProvider` for?"
    **Short answer:** Lazy or optional injection — get a bean if available, a new prototype each call, or iterate candidates — without failing startup when it's absent. **Ch 02, 41.**

??? question "B2 · How do you exclude an auto-configuration?"
    **Short answer:** `spring.autoconfigure.exclude` or `@SpringBootApplication(exclude = …)`. If you need it often, the starter is missing a property toggle or `@ConditionalOnMissingBean`. **Ch 05, 41.**

??? question "B2 · How do profile groups help?"
    **Short answer:** They compose several profiles under one name (`prod` → `prod-db`, `prod-kafka`), keeping activation simple and configuration modular. **Ch 06.**

??? question "B2 · How do you keep secrets out of `/actuator/env` output?"
    **Short answer:** Boot sanitizes keys that look like secrets; restrict the endpoint's exposure, keep it on the management port, and use `show-values: never` or `when-authorized`. **Ch 06, 27.**

??? question "B2 · Why mount a ConfigMap as a file rather than dozens of env vars?"
    **Short answer:** A YAML file supports maps and lists, avoids env-var name mangling, is reviewable as one unit, and triggers a rollout via a config hash. **Ch 06, 30.**

### Web, validation, JSON

??? question "B2 · How do you validate path and query parameters?"
    **Short answer:** Put constraints on the parameters and annotate the controller class with `@Validated`; violations produce `ConstraintViolationException`, which the advice maps to 400. **Ch 09.**

??? question "B2 · How do you return field-level validation errors in a stable format?"
    **Short answer:** Map `MethodArgumentNotValidException` in the advice to a problem body with an `errors` array of `{field, code, message}`, using message codes rather than raw text. **Ch 09, 10.**

??? question "B2 · How do you version error codes without breaking clients?"
    **Short answer:** Treat codes as a public contract: add new ones freely, never repurpose or rename existing ones, and publish a generated catalog. **Ch 10, 20.**

??? question "B2 · How do you customize the ObjectMapper without losing Boot's defaults?"
    **Short answer:** Use `spring.jackson.*` properties or a `Jackson2ObjectMapperBuilderCustomizer` (or its Jackson 3 equivalent) rather than defining a new `ObjectMapper` bean from scratch. **Ch 11.**

??? question "B2 · What's the danger of `@JsonIgnoreProperties(ignoreUnknown = false)` on consumers?"
    **Short answer:** Any new field from the producer breaks deserialization; tolerant readers ignore unknown fields so producers can evolve additively. **Ch 11, 23.**

??? question "B2 · How do you return 201 with a Location header?"
    **Short answer:** `ResponseEntity.created(uri).body(view)`, building the URI with `ServletUriComponentsBuilder.fromCurrentRequest().path("/{ref}")`. **Ch 08.**

### Data

??? question "B2 · When would you use `JdbcClient` over JPA in the same service?"
    **Short answer:** For reporting queries, bulk updates, hot read paths or anything where you want exact SQL and no persistence-context overhead. **Ch 12.**

??? question "B2 · What is `@Modifying` and its pitfall?"
    **Short answer:** Marks an update/delete JPQL query. It bypasses the persistence context, so loaded entities become stale unless you clear or refresh them. **Ch 13.**

??? question "B2 · Why set `@ManyToOne(fetch = LAZY)` explicitly?"
    **Short answer:** `@ManyToOne` defaults to eager loading, which silently adds joins or queries everywhere the entity is loaded. **Ch 13.**

??? question "B2 · How do batch inserts work in Hibernate?"
    **Short answer:** Set `hibernate.jdbc.batch_size` with ordered inserts/updates; avoid `IDENTITY` generation, which disables insert batching — use sequences. **Ch 13.**

??? question "B2 · How should a Flyway migration be written for a large table?"
    **Short answer:** Additive and backward compatible, with concurrent index creation and batched backfills, rehearsed on production-sized data. **Ch 14.**

??? question "B2 · What does `@Transactional(readOnly = true)` buy you?"
    **Short answer:** Hibernate skips dirty checking and flushes, and drivers or routing can use replicas. It isn't a security control. **Ch 16.**

??? question "B2 · How do you route reads to a replica?"
    **Short answer:** A routing `DataSource` keyed on transaction read-only status, accepting replica lag — never for reads that must see a just-committed write. **Ch 12.**

### Security

??? question "B2 · How do you test a secured endpoint with a JWT?"
    **Short answer:** `spring-security-test`'s `jwt()` post-processor (or `mockJwt()` for WebFlux) with claims and authorities, plus at least one integration test with a really signed token. **Ch 18.**

??? question "B2 · How do you map token claims to roles?"
    **Short answer:** A `JwtAuthenticationConverter` combining scope authorities with an allow-listed mapping from a roles claim to `ROLE_*`. **Ch 18.**

??? question "B2 · How do you rate-limit OTP login?"
    **Short answer:** Separate limits on OTP requests and verification attempts, per mobile and per IP, in a shared store like Redis, with lockout and alerting. **Ch 17, 22.**

??? question "B2 · Why store refresh tokens hashed?"
    **Short answer:** A database leak must not yield usable credentials; store a hash with family and device metadata, and rotate on use. **Ch 18.**

??? question "B2 · How should CORS be configured with Spring Security?"
    **Short answer:** Through `http.cors(...)` with a `CorsConfigurationSource`, listing exact origins, so preflight requests are handled before authentication. **Ch 17.**

### Clients, caching, NoSQL

??? question "B2 · How do you propagate trace context to downstream calls?"
    **Short answer:** Build clients from Boot's injected builders; Micrometer Tracing adds `traceparent` automatically. Add your correlation id with an interceptor. **Ch 19, 27.**

??? question "B2 · Why disable automatic retries in the Apache HTTP client?"
    **Short answer:** Retries are a policy decision (idempotency, budgets, one layer) made explicitly above the client, not silently inside it. **Ch 19, 26.**

??? question "B2 · Caffeine or Redis for a cache?"
    **Short answer:** Caffeine for tiny, hot, staleness-tolerant data per pod; Redis when consistency across pods or survival across restarts matters. **Ch 21.**

??? question "B2 · Should you cache null results?"
    **Short answer:** Often, briefly, to stop repeated misses for non-existent keys — with explicit eviction when the entity appears. **Ch 21.**

??? question "B2 · How do you warm a cache without slowing readiness too much?"
    **Short answer:** Warm only the top-N keys in a runner before readiness; fill the rest lazily or asynchronously. **Ch 21, 29.**

??? question "B2 · Why use `StringRedisTemplate` instead of a raw `RedisTemplate`?"
    **Short answer:** Readable string keys and values, no JDK serialization, and no class-instantiation risks from payloads. **Ch 22.**

### Messaging and async

??? question "B2 · How do you choose a Kafka message key?"
    **Short answer:** The aggregate id whose events must stay ordered (order reference, SKU), which also co-locates them on one partition. **Ch 23.**

??? question "B2 · What does `auto.offset.reset` control?"
    **Short answer:** Where a consumer group with no committed offset starts: `earliest` to process history, `latest` for live-only feeds. **Ch 23.**

??? question "B2 · Why disable topic auto-creation in production?"
    **Short answer:** Auto-created topics get default partitions, replication and retention nobody reviewed; topics are infrastructure. **Ch 23.**

??? question "B2 · What is a batch listener good for?"
    **Short answer:** Throughput when handling items together is cheaper — bulk indexing, bulk inserts — with idempotent processing and careful error handling. **Ch 23.**

??? question "B2 · How do you propagate MDC and security context to `@Async` tasks?"
    **Short answer:** A `TaskDecorator` (context propagation) and `DelegatingSecurityContextExecutor` on the executor; transactions never propagate and shouldn't. **Ch 07, 17, 25.**

??? question "B2 · Why prefer a sweeper over per-order timers?"
    **Short answer:** A periodic query with `SKIP LOCKED` is idempotent, self-healing after downtime and needs no per-entity state. **Ch 25.**

### Resilience, observability, testing, operations

??? question "B2 · What's a good fallback, and what's a bad one?"
    **Short answer:** Good: last-known values with a staleness bound, simpler computations, queue-for-later. Bad: invented prices or payment results, or catching everything and returning empty results. **Ch 26.**

??? question "B2 · How do you expose a custom business metric?"
    **Short answer:** A Micrometer counter, timer or summary with low-cardinality tags (channel, payment method), registered once and tested. **Ch 27.**

??? question "B2 · How do you write a health indicator that shouldn't affect readiness?"
    **Short answer:** Implement `HealthIndicator`, return a custom status like `DEGRADED` with details, and leave it out of the readiness group. **Ch 27.**

??? question "B2 · Why assert async behaviour with Awaitility rather than sleeps?"
    **Short answer:** Sleeps are either too short (flaky) or too long (slow); Awaitility polls until the condition holds or a timeout expires. **Ch 15.**

??? question "B2 · How do you share containers across test classes?"
    **Short answer:** Declare them as beans in a shared `@TestConfiguration` with `@ServiceConnection`, and keep context configuration consistent so the context cache reuses them. **Ch 15, 28.**

??? question "B2 · What's `startupProbe` for?"
    **Short answer:** Giving slow-starting pods time to boot without making the liveness probe lenient forever. **Ch 30.**

??? question "B2 · Why is `maxUnavailable: 0` common for request-serving services?"
    **Short answer:** Rolling updates never reduce serving capacity below the current replica count. **Ch 30.**

??? question "B2 · Why must `maxReplicas` consider the database?"
    **Short answer:** Every pod brings a connection pool; `pods × pool × services` must fit `max_connections`. **Ch 12, 30.**

---

[:material-arrow-left: B1 · 0–2 years](b1-0-2-years.md) · [B3 · 5–8 years :material-arrow-right:](b3-5-8-years.md)
