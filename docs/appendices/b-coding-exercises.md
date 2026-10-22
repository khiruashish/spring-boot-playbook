# Appendix B · Coding Exercises

Graded exercises that complement the capstone milestones (Chapter 44). Each has a **task**, **acceptance criteria** you can verify with tests, **hints**, and a **reference solution sketch**. They're sized for 30 minutes (B1) to a day (B5).

## How to use these

| Goal | Approach |
|---|---|
| Learning | Do the exercises for your band and the one above; compare with the solution only after your tests pass |
| Interview practice | Time-box to the suggested duration; explain your choices aloud |
| Interviewing others | Pair on one exercise; the conversation matters more than completion |
| Team onboarding | Assign B1–B2 exercises in the first two weeks |

**Rule for every exercise**: the acceptance criteria are tests. If you can't write the test, you haven't understood the requirement.

## Index

| # | Exercise | Band | Time | Chapters |
|---|---|---|---|---|
| B-01 | Pincode validator | B1 | 30 min | 09 |
| B-02 | Product API with problem details | B1 | 1 h | 08, 10 |
| B-03 | Money value object | B1 | 30 min | 11, 37 |
| B-04 | Cart with ETags | B2 | 2 h | 08, 16 |
| B-05 | Idempotent order creation | B2 | 2 h | 04 |
| B-06 | Cached pricing with fail-open | B2 | 2 h | 21 |
| B-07 | Resilient HTTP client | B2 | 2 h | 19, 26 |
| B-08 | Outbox and relay | B3 | 3 h | 23, 36 |
| B-09 | Idempotent Kafka consumer | B3 | 2 h | 23 |
| B-10 | Query-count-guarded order history | B3 | 2 h | 13, 34 |
| B-11 | Restartable batch job | B3 | 4 h | 33 |
| B-12 | Ownership authorization | B3 | 2 h | 17 |
| B-13 | Checkout saga | B4 | 1 day | 36 |
| B-14 | Tenant leak suite | B4 | 4 h | 38 |
| B-15 | Platform starter | B4 | 4 h | 41 |
| B-16 | Load test and fix | B4 | 4 h | 34 |
| B-17 | Upgrade a service | B5 | 1 day | 42 |
| B-18 | Design review and ADR | B5 | 3 h | 43 |

---

## B1 exercises

### B-01 · Pincode validator

**Task**: Create `@Pincode`, a Jakarta constraint for Indian pincodes (six digits, first digit 1–9), usable on fields and parameters.

**Acceptance criteria**
- `560102` and `744101` are valid; `060102`, `56010`, `5601021`, `56O102` are invalid.
- `null` is valid (combine with `@NotNull` when required).
- The error message is resolvable from a message bundle.

??? tip "Hints"
    A `@Constraint(validatedBy = …)` annotation plus a `ConstraintValidator<Pincode, String>`; a precompiled `Pattern`. **Ch 09.**

??? success "Solution sketch"
    ```java
    @Documented
    @Constraint(validatedBy = PincodeValidator.class)
    @Target({FIELD, PARAMETER, RECORD_COMPONENT})
    @Retention(RUNTIME)
    public @interface Pincode {
        String message() default "{grocery.validation.pincode}";
        Class<?>[] groups() default {};
        Class<? extends Payload>[] payload() default {};
    }

    public class PincodeValidator implements ConstraintValidator<Pincode, String> {
        private static final Pattern VALID = Pattern.compile("[1-9][0-9]{5}");
        @Override public boolean isValid(String value, ConstraintValidatorContext ctx) {
            return value == null || VALID.matcher(value).matches();
        }
    }
    ```
    ```java
    @ParameterizedTest
    @ValueSource(strings = {"060102", "56010", "5601021", "56O102"})
    void rejectsInvalid(String value) {
        assertThat(validator.validate(new Req(value))).hasSize(1);
    }
    ```

### B-02 · Product API with problem details

**Task**: `GET /api/v1/products/{sku}` and `GET /api/v1/products?category=&page=&size=` backed by PostgreSQL, returning RFC 9457 problems for unknown SKUs and invalid parameters.

**Acceptance criteria**
- Unknown SKU → 404 `application/problem+json` with `code: PRODUCT_NOT_FOUND`.
- `size > 100` → 400 with a field error.
- Pages have a stable envelope (`items`, `page`, `size`, `totalItems`, `hasNext`).
- `@WebMvcTest` for the controller; one Testcontainers test for the repository.

??? tip "Hints"
    A `@RestControllerAdvice` mapping a `ProductNotFoundException` to `ProblemDetail`; `@Validated` on the controller with `@Max(100)` on `size`. **Ch 08, 10, 15.**

??? success "Solution sketch"
    ```java
    @RestControllerAdvice
    class ErrorHandler {
        @ExceptionHandler(ProductNotFoundException.class)
        ProblemDetail notFound(ProductNotFoundException e) {
            var p = ProblemDetail.forStatusAndDetail(NOT_FOUND, "Product %s not found".formatted(e.sku()));
            p.setType(URI.create("https://errors.grocery.in/product-not-found"));
            p.setProperty("code", "PRODUCT_NOT_FOUND");
            return p;
        }
    }
    ```

### B-03 · Money value object

**Task**: An immutable `Money` in INR with addition, multiplication by quantity, comparison and JSON serialization as a decimal string.

**Acceptance criteria**
- `Money.rupees("0.10").plus(Money.rupees("0.20"))` equals `Money.rupees("0.30")`.
- Negative amounts are rejected at construction.
- Scale normalized to 2 with `HALF_UP`.
- Serialized as `"578.00"`, not `578.0`.
- `Money.rupees("1.0")` equals `Money.rupees("1.00")`.

??? success "Solution sketch"
    A record with a compact constructor normalizing scale and rejecting negatives; equality works because scale is normalized. Use `@JsonValue` on a `toString()` returning `amount.toPlainString()` and a `@JsonCreator` factory. **Ch 11, 37.**

---

## B2 exercises

### B-04 · Cart with ETags

**Task**: Cart endpoints returning a strong ETag; mutations require `If-Match`.

**Acceptance criteria**
- `GET /carts/{id}` returns `ETag: "3"` (the version).
- `POST /carts/{id}/items` without `If-Match` → 428; stale → 412; current → 200 with a new ETag.
- Concurrent updates with the same ETag: exactly one succeeds.
- `Cart` invariants (≤ 50 lines, 1–20 per line) tested without Spring.

??? tip "Hints"
    JPA `@Version` as the ETag source; compare before mutating and let optimistic locking catch the race. **Ch 08, 16, 37.**

??? success "Solution sketch"
    ```java
    @PostMapping("/{id}/items")
    ResponseEntity<CartView> add(@PathVariable UUID id,
                                 @RequestHeader(value = HttpHeaders.IF_MATCH, required = false) String ifMatch,
                                 @Valid @RequestBody AddItem req) {
        if (ifMatch == null) throw new PreconditionRequiredException();
        CartView view = delegate.addItem(id, parseVersion(ifMatch), req);   // throws StaleVersion → 412
        return ResponseEntity.ok().eTag("\"" + view.version() + "\"").body(view);
    }
    ```
    The concurrency test submits two updates with the same version on virtual threads and asserts one 200 and one 412.

### B-05 · Idempotent order creation

**Task**: `POST /orders` requires an `Idempotency-Key`; repeated requests return the original response without creating a second order.

**Acceptance criteria**
- Same key + same body → same response, one order row.
- Same key + different body → 422 `IDEMPOTENCY_KEY_REUSED`.
- Concurrent duplicates → one order.
- Keys expire after 24 h.

??? tip "Hints"
    A table `idempotency_record(key primary key, request_hash, response, created_at)`; insert first in the transaction so a concurrent duplicate hits the unique key. **Ch 04.**

### B-06 · Cached pricing with fail-open

**Task**: Cache `priceFor(sku, pincode)` in Redis with a 2-minute jittered TTL; Redis failures must not fail requests.

**Acceptance criteria**
- Second call hits the cache (repository spy called once).
- Different pincodes are different keys.
- Stopping Redis: calls still succeed; `grocery.cache.errors` increments.
- Evicting after a price change happens after commit.

??? success "Solution sketch"
    `@Cacheable(cacheNames = "price", key = "#sku + '|' + #pincode")`; a `CachingConfigurer` returning a `CacheErrorHandler` that logs and meters; eviction via `@TransactionalEventListener(phase = AFTER_COMMIT)`. **Ch 21.**

### B-07 · Resilient HTTP client

**Task**: An inventory client via an HTTP interface with 400 ms read timeout, one jittered retry for timeouts, a circuit breaker, and a fallback for shelf-stable items.

**Acceptance criteria**
- WireMock delay of 2 s → call returns within 1 s with a `DependencyException` (perishable) or the fallback (shelf-stable).
- 404 → `Optional.empty()`, not an exception.
- After 20 failures the breaker is OPEN and calls return in < 50 ms.
- No retry on 4xx.

??? tip "Hints"
    Configure the request factory timeouts; `@Retry` wrapping `@CircuitBreaker`; ignore domain exceptions in the breaker. **Ch 19, 26, 28.**

---

## B3 exercises

### B-08 · Outbox and relay

**Task**: Implement the outbox table, a `MANDATORY` writer, and a polling relay using `SKIP LOCKED`.

**Acceptance criteria**
- Writing outside a transaction throws.
- A failure after both inserts leaves neither the order nor the outbox row.
- Two relay instances never publish the same row concurrently.
- A broker outage leaves rows pending; they publish on recovery.
- `grocery.outbox.pending` gauge exposed.

??? success "Solution sketch"
    ```sql
    select id, aggregate_type, aggregate_id, event_type, payload, headers
    from outbox where sent_at is null
    order by id limit 200
    for update skip locked;
    ```
    Publish each row, `get()` the send future with a timeout, mark sent; stop the batch on the first failure to preserve per-aggregate order. **Ch 23, 36.**

### B-09 · Idempotent Kafka consumer

**Task**: An inventory consumer for `OrderPlaced` that reserves stock exactly once per event, with DLT for malformed messages.

**Acceptance criteria**
- The same event delivered twice → one reservation (Testcontainers Kafka).
- Malformed JSON → DLT, partition continues.
- Transient DB failure → retried with back-off.
- Inbox rows older than 7 days are cleaned up.

??? tip "Hints"
    Inbox insert in the same transaction as the reservation; `ErrorHandlingDeserializer` + `DefaultErrorHandler` with non-retryable classification. **Ch 23.**

### B-10 · Query-count-guarded order history

**Task**: `GET /customers/{id}/orders` returns 20 orders with lines and product names in at most 2 queries, with p95 < 300 ms at 150 req/s.

**Acceptance criteria**
- Query-count test asserts ≤ 2 selects.
- Composite index verified with `EXPLAIN` in a test on Testcontainers.
- k6 open-model test with a p95 threshold.

??? success "Solution sketch"
    A DTO projection or `@EntityGraph(attributePaths = {"lines"})` with keyset pagination on `(customer_id, placed_at desc)`; Hibernate statistics or a datasource proxy counting statements. **Ch 13, 34.**

### B-11 · Restartable batch job

**Task**: A catalog CSV import job with skips (≤ 100), a rejects file, and restart from the failure point.

**Acceptance criteria**
- 10,000 rows with 25 malformed → COMPLETED, 25 in the rejects file with reasons.
- Injected failure at row 6,000, then restart with the same parameters → exactly 10,000 rows, no duplicates.
- More than 100 bad rows → FAILED with a clear exit status.

??? tip "Hints"
    `faultTolerant().skip(...).skipLimit(100)`, a `SkipListener` writing rejects, idempotent upsert writer, named reader. **Ch 33.**

### B-12 · Ownership authorization

**Task**: Customers can read only their own orders; ops staff can read any; sellers only orders containing their products.

**Acceptance criteria**
- A parameterized access-matrix test covering anonymous (401), other customer (403 or 404), owner (200), ops (200), seller with and without items (200/403).
- The check is enforced in one reusable `AuthorizationManager` or query scope.

??? success "Solution sketch"
    Owner-scoped queries for customers (`findByRefAndCustomerId`), an `AuthorizationManager` for sellers checking line ownership, `hasRole('OPS')` bypass, and the matrix test as the executable policy. **Ch 17, 39.**

---

## B4 exercises

### B-13 · Checkout saga

**Task**: Implement an orchestrated saga: reserve stock → authorize payment → confirm, with compensations and deadlines.

**Acceptance criteria**
- Happy path → saga COMPLETED, order PAID.
- Payment failure → stock released, order CANCELLED, saga COMPENSATED.
- Duplicate failure event → exactly one release command.
- `PaymentAuthorized` before `StockReserved` → ignored, counted.
- Deadline passed → compensation; repeated compensation failure → STUCK + alert.
- Late `PaymentAuthorized` after compensation → void issued.

??? tip "Hints"
    Saga table with a version column; guarded transitions; commands via the outbox; a ShedLock-protected sweeper; a controllable `Clock`. **Ch 36.**

??? success "Solution sketch"
    See Chapter 36 §5.3 for the state machine and §6.5 for the test suite; the late-authorization case is an extra handler that, when the saga is terminal, emits `VoidPaymentCommand` instead of transitioning.

### B-14 · Tenant leak suite

**Task**: Add tenancy to two services and a reflective leak suite.

**Acceptance criteria**
- Every repository `find*` method with no parameters returns only the current tenant's rows.
- A native query is still filtered (RLS).
- A pooled connection used for tenant A then B reports B's setting.
- `@Async` and Kafka paths keep the tenant.
- Missing tenant → exception, zero rows.

??? tip "Hints"
    `@TenantId`, forced RLS with `with check`, `TaskDecorator`, Kafka header, and reflection over `CrudRepository` beans. **Ch 38.**

### B-15 · Platform starter

**Task**: Build `grocery-platform-web-spring-boot-starter` providing the correlation filter and problem-details handler.

**Acceptance criteria**
- Both beans are present by default in a servlet app and absent in a non-web app.
- Each backs off when the user defines their own.
- Disabled by `grocery.web.enabled=false`.
- Works without Micrometer Tracing on the classpath (`FilteredClassLoader`).
- Invalid property fails with a message naming it.
- IDE metadata generated.

??? success "Solution sketch"
    Chapter 41 §4.2–§5.5: `@AutoConfiguration`, `compileOnly` dependencies, imports file, `@ConditionalOnMissingBean` everywhere, `ApplicationContextRunner` tests.

### B-16 · Load test and fix

**Task**: Given a deliberately slow service (N+1, missing index, DEBUG string concatenation, remote call inside a transaction), find and fix the bottlenecks.

**Acceptance criteria**
- An open-model k6 test with thresholds that fails before and passes after.
- A wall-clock profile before and after, with the findings explained.
- Each fix accompanied by a guard (query-count test, index check, ArchUnit rule for transactions).

??? tip "Hints"
    Measure first; fix the widest frame; re-measure. None of the fixes is a JVM flag. **Ch 34.**

---

## B5 exercises

### B-17 · Upgrade a service

**Task**: Upgrade one capstone service from Boot 3.5 to 4.x using the Chapter 42 process.

**Acceptance criteria**
- Deprecations at zero before the version change.
- OpenRewrite patch attached and reviewed.
- Properties migrator output resolved, then removed.
- Golden-file, access-matrix and contract tests unchanged.
- Cross-version Kafka and cache compatibility tests pass.
- Performance within 10% of baseline.
- A short retrospective: what broke, what the tests caught, what they missed.

### B-18 · Design review and ADR

**Task**: Review a colleague's RFC proposing to replace the polling outbox with Debezium CDC for all services.

**Acceptance criteria**
- Written review with labelled comments (blocking/suggestion/question).
- Identification of the replication-slot risk and required safeguards.
- A recommendation with conditions (which services, triggers, prerequisites).
- An ADR recording the decision with a revisit trigger.

??? success "What a strong answer includes"
    Supports CDC for high-volume services only; requires slot-lag and WAL alerts, `max_slot_wal_keep_size`, a runbook and a staging downtime test; keeps polling as the default; records the decision with a trigger (events/s or latency) and an owner. **Ch 36, 43.**

---

[:material-arrow-left: A Interview Bank](a-interview-bank/index.md) · [C Annotation Cheat Sheet :material-arrow-right:](c-annotation-cheat-sheet.md)
