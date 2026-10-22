# B1 · 0–2 Years

Vocabulary and mechanics. A strong B1 candidate knows what each piece is, can use it correctly in a simple case, and knows where to look when it doesn't work.

## Java and build

??? question "B1 · What is a Spring Boot executable JAR?"
    **Short answer:** A JAR containing your classes, all dependencies under `BOOT-INF/lib`, and a launcher that sets up the classpath and calls your `main` method — runnable with `java -jar`. **Ch 01, 29.**

??? question "B1 · What does a BOM do in a Gradle or Maven build?"
    **Short answer:** It pins versions for a set of related dependencies so you declare them without versions and get a tested, compatible combination. **Ch 01.**

??? question "B1 · What is a Java record, and where is it useful in Spring applications?"
    **Short answer:** An immutable data carrier with generated constructor, accessors, `equals`, `hashCode` and `toString`. Ideal for DTOs, configuration properties, events and value objects. **Ch 01, 06, 37.**

??? question "B1 · Why use `BigDecimal` for money?"
    **Short answer:** `double` cannot represent most decimal fractions exactly, so sums drift (₹0.1 + ₹0.2 ≠ ₹0.3). `BigDecimal` gives exact decimal arithmetic with explicit rounding. **Ch 01, 11.**

## Spring core

??? question "B1 · What is dependency injection?"
    **Short answer:** Objects receive their collaborators from the container instead of creating them, which makes code loosely coupled and testable. **Ch 02.**

??? question "B1 · Why prefer constructor injection?"
    **Short answer:** Dependencies are explicit and final, objects are never half-initialized, and tests can construct the class without Spring. **Ch 02.**

??? question "B1 · What is a bean?"
    **Short answer:** An object whose lifecycle is managed by the Spring container — created, wired, and destroyed by it. **Ch 02.**

??? question "B1 · What's the difference between `@Component`, `@Service` and `@Repository`?"
    **Short answer:** All register beans through scanning; `@Service` and `@Repository` communicate intent, and `@Repository` also enables persistence exception translation. **Ch 02, 12.**

??? question "B1 · What is the default bean scope?"
    **Short answer:** Singleton — one instance per application context. Singletons must therefore be stateless or thread-safe. **Ch 02.**

??? question "B1 · What does `@PostConstruct` do?"
    **Short answer:** Runs a method after dependencies are injected, for initialization that needs them. **Ch 03.**

??? question "B1 · What is AOP used for in Spring?"
    **Short answer:** Applying cross-cutting behaviour — transactions, security, caching, retries, logging — around method calls without changing the methods. **Ch 04.**

## Spring Boot fundamentals

??? question "B1 · What does `@SpringBootApplication` combine?"
    **Short answer:** `@Configuration`, `@EnableAutoConfiguration` and `@ComponentScan` from the class's package downwards. **Ch 05.**

??? question "B1 · What is auto-configuration?"
    **Short answer:** Boot configures beans automatically based on what's on the classpath and in properties, and backs off when you define your own. **Ch 05, 41.**

??? question "B1 · What is a starter?"
    **Short answer:** A dependency that brings in a coherent set of libraries (and their auto-configuration) for a capability, such as `spring-boot-starter-web`. **Ch 05, 41.**

## Configuration and logging

??? question "B1 · How do profiles work?"
    **Short answer:** Named sets of configuration (`application-prod.yml`) activated with `spring.profiles.active`, letting the same artifact run differently per environment. **Ch 06.**

??? question "B1 · Why use `@ConfigurationProperties` instead of `@Value`?"
    **Short answer:** Typed, grouped, validated configuration with IDE metadata, rather than scattered string lookups. **Ch 06.**

??? question "B1 · Where should secrets like database passwords come from?"
    **Short answer:** A secret manager, mounted as files and read as a config tree — never committed to Git or baked into images. **Ch 06, 39.**

??? question "B1 · Why use parameterized log messages?"
    **Short answer:** `log.debug("Order {}", ref)` avoids building the string when the level is disabled; concatenation always pays the cost. **Ch 07, 34.**

??? question "B1 · Why should logs be structured (JSON) in production?"
    **Short answer:** Log platforms can index and search fields like `traceId`, `tenantId` and `orderRef` reliably, instead of parsing free text. **Ch 07.**

## Web layer

??? question "B1 · `@Controller` vs `@RestController`?"
    **Short answer:** `@RestController` adds `@ResponseBody` to every method, so return values are serialized (usually to JSON) rather than resolved as views. **Ch 08.**

??? question "B1 · Which status code should creating a resource return?"
    **Short answer:** `201 Created` with a `Location` header pointing at the new resource. **Ch 08.**

??? question "B1 · `@PathVariable` vs `@RequestParam`?"
    **Short answer:** Path variables identify a resource (`/orders/{ref}`); request parameters filter, sort or paginate (`?page=0&size=20`). **Ch 08.**

??? question "B1 · How do you validate a request body?"
    **Short answer:** Add Jakarta constraints to the DTO (`@NotBlank`, `@Size`, `@Min`) and annotate the parameter with `@Valid`. **Ch 09.**

??? question "B1 · What is a problem-details response?"
    **Short answer:** A standard error body (RFC 9457) with `type`, `title`, `status`, `detail` and `instance`, which Spring supports via `ProblemDetail`. **Ch 10.**

??? question "B1 · Why shouldn't you return `200` with an error in the body?"
    **Short answer:** Clients, caches, monitoring and retries all key off status codes; hiding failures in a 200 breaks them. **Ch 10, 20.**

??? question "B1 · Why not expose JPA entities directly in API responses?"
    **Short answer:** It couples the API to the database schema, risks lazy-loading errors and leaks internal fields. Use DTOs. **Ch 11, 13.**

## Data

??? question "B1 · What does a connection pool do?"
    **Short answer:** Reuses database connections instead of opening one per request, which is expensive. HikariCP is Boot's default. **Ch 12.**

??? question "B1 · What is SQL injection and how do you prevent it?"
    **Short answer:** User input interpreted as SQL. Prevent it with parameterized queries — never string concatenation. **Ch 12, 39.**

??? question "B1 · What is the N+1 problem?"
    **Short answer:** Loading a list with one query, then issuing one more query per item for a relationship — 1 + N queries instead of one or two. **Ch 13.**

??? question "B1 · Why use Flyway or Liquibase instead of `ddl-auto=update`?"
    **Short answer:** Versioned, reviewed, repeatable migrations applied the same way in every environment, instead of unpredictable schema changes generated at startup. **Ch 14.**

??? question "B1 · What does `@Transactional` do?"
    **Short answer:** Runs the method in a database transaction — commit on success, rollback on (unchecked) exceptions. **Ch 16.**

## Security

??? question "B1 · Authentication vs authorization?"
    **Short answer:** Authentication establishes who you are; authorization decides what you may do. **Ch 17.**

??? question "B1 · 401 vs 403?"
    **Short answer:** 401: not authenticated (missing or invalid credentials). 403: authenticated but not allowed. **Ch 17.**

??? question "B1 · How should passwords be stored?"
    **Short answer:** Hashed with a slow, salted algorithm such as BCrypt or Argon2 via `DelegatingPasswordEncoder` — never plaintext or plain hashes. **Ch 17.**

??? question "B1 · What is a JWT, and is it encrypted?"
    **Short answer:** A signed token with a header, claims and signature. It is **signed, not encrypted** — anyone can read the claims, so no secrets or PII belong in it. **Ch 18.**

??? question "B1 · Why should the server compute order totals rather than trust the client?"
    **Short answer:** Anything sent by a client can be modified. Prices, discounts and totals must come from authoritative server-side data. **Ch 39.**

## HTTP clients, APIs, caching

??? question "B1 · Which HTTP client should new Spring code use?"
    **Short answer:** `RestClient` (or a declarative HTTP interface backed by it) for synchronous calls; `WebClient` for reactive. `RestTemplate` is in maintenance. **Ch 19.**

??? question "B1 · Why must every outbound HTTP call have a timeout?"
    **Short answer:** Without one, a slow dependency holds threads and connections indefinitely and can take your service down. **Ch 19, 26.**

??? question "B1 · What does `@Cacheable` do?"
    **Short answer:** Returns a cached result when the key is present; otherwise calls the method and stores the result. Requires `@EnableCaching`. **Ch 21.**

??? question "B1 · What's a backward-compatible API change?"
    **Short answer:** Adding an optional request field, a response field, or a new endpoint — existing clients keep working. **Ch 20.**

## Messaging and async

??? question "B1 · What is a Kafka topic, partition and consumer group?"
    **Short answer:** A topic is a named log split into ordered partitions; each partition is read by one consumer per group; each group gets every message. **Ch 23.**

??? question "B1 · What delivery guarantee does Kafka provide by default?"
    **Short answer:** At-least-once — messages may be redelivered, so consumers must be idempotent. **Ch 23.**

??? question "B1 · How is RabbitMQ different from Kafka?"
    **Short answer:** RabbitMQ is a queue with flexible routing — messages are removed once acknowledged. Kafka is a retained log — consumers track offsets and can replay. **Ch 24.**

??? question "B1 · What does `@Async` do?"
    **Short answer:** Runs the method on another thread from an executor, returning immediately. Requires `@EnableAsync` and a call through the proxy. **Ch 25.**

??? question "B1 · `fixedDelay` vs `fixedRate` in `@Scheduled`?"
    **Short answer:** `fixedDelay` waits after the previous run finishes (no overlap); `fixedRate` starts on a fixed schedule regardless of duration. **Ch 25.**

## Testing, packaging, operations

??? question "B1 · Unit test vs integration test?"
    **Short answer:** A unit test checks one class in isolation, fast and without infrastructure; an integration test checks components working together with real infrastructure. **Ch 15, 28.**

??? question "B1 · What is `@WebMvcTest`?"
    **Short answer:** A test slice loading only the web layer — controllers, advice, converters — with collaborators mocked. **Ch 15.**

??? question "B1 · Why use Testcontainers instead of H2?"
    **Short answer:** It runs the real database in Docker, so SQL, types and locking behave as in production. **Ch 15, 28.**

??? question "B1 · Why shouldn't containers run as root?"
    **Short answer:** It limits the damage of a compromise and is required by most cluster security policies. **Ch 29.**

??? question "B1 · Readiness vs liveness probes?"
    **Short answer:** Readiness decides whether the pod receives traffic; liveness decides whether it's restarted. Liveness must not check dependencies. **Ch 30.**

## Observability and resilience

??? question "B1 · What does Spring Boot Actuator provide?"
    **Short answer:** Production endpoints: health (with probe groups), info, metrics/Prometheus, loggers, startup, env and more. **Ch 27.**

??? question "B1 · Why look at p99 latency rather than the average?"
    **Short answer:** Averages hide the slow tail that real users experience; p99 shows how bad it gets for 1 in 100 requests. **Ch 27, 34.**

??? question "B1 · What does a circuit breaker do?"
    **Short answer:** After repeated failures, it stops calling a dependency and fails fast (or falls back), then tries again later to see if it recovered. **Ch 26.**

??? question "B1 · When is it safe to retry a call?"
    **Short answer:** For idempotent operations failing transiently (timeouts, 5xx) — never blindly for non-idempotent writes such as payments. **Ch 19, 26.**

---

[:material-arrow-left: Interview Bank](index.md) · [B2 · 2–5 years :material-arrow-right:](b2-2-5-years.md)
