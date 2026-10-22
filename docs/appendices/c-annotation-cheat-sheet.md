# Appendix C · Annotation Cheat Sheet

!!! tip "Want examples?"
    This page is the one-line lookup. The **[Annotations](../annotations/index.md)** tab has every annotation with a grocery-platform example, its package, status and pitfalls — plus the full [Outdated → Replacement](../annotations/deprecated.md) list.

The annotations used throughout the handbook, grouped by area, with what each does, the pitfall that matters, and where it's explained. Proxy-based annotations are marked **(proxy)** — they need calls to go through the Spring proxy: public methods, no self-invocation (Chapter 04).

## C.1 Core container

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@Component` / `@Service` / `@Repository` / `@Controller` | Register a bean via scanning | `@Repository` also translates persistence exceptions | 02 |
| `@Configuration(proxyBeanMethods = false)` | Declare `@Bean` methods | Use `false` unless beans call each other's methods | 02 |
| `@Bean` | Define a bean from a method | `static` for `BeanFactoryPostProcessor`s | 02, 03 |
| `@Primary` | Default among multiple candidates | Hides ambiguity — prefer explicit qualifiers for important choices | 02 |
| `@Qualifier` | Select a specific bean | Keep names stable | 02 |
| `@Scope("prototype")` | New instance per lookup | Injected into a singleton only once — use `ObjectProvider` | 02 |
| `@Lazy` | Create on first use | Moves failures from startup to runtime | 02, 03 |
| `@Profile` | Activate by profile | Prefer properties for feature flags | 06 |
| `@Import` | Include configuration classes | Library code shouldn't rely on the user's component scan | 41 |
| `@PostConstruct` / `@PreDestroy` | Init / destroy callbacks | Run on the target, not through proxies | 03 |
| `@EventListener` | Handle application events | Runs inside the publisher's transaction | 03 |
| `@TransactionalEventListener` | Handle events at a transaction phase (default after commit) | Needs `REQUIRES_NEW` if it writes to the DB | 03, 16 |
| `@Order` | Ordering of beans, filters, chains | Lower value = higher precedence | 17 |
| `@DependsOn` | Force initialization order | Usually a design smell | 03 |

## C.2 Spring Boot

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@SpringBootApplication` | Configuration + auto-configuration + scanning | Scans only its package and below | 05 |
| `@ConfigurationProperties(prefix)` | Typed configuration | Enable via `@EnableConfigurationProperties` or scanning | 06 |
| `@EnableConfigurationProperties` | Register properties classes | Use in auto-configuration | 06, 41 |
| `@Validated` (on properties) | Validate at startup | Fails fast with a property name | 06 |
| `@DefaultValue` | Default for constructor-bound properties | Keeps records immutable | 06, 41 |
| `@DeprecatedConfigurationProperty` | Mark a property deprecated with replacement | Keep the old one working for a major | 41 |
| `@AutoConfiguration(before/after)` | Auto-configuration class | Never plain `@Configuration` | 41 |
| `@ConditionalOnClass` / `OnMissingClass` | Library presence | Dependencies must be optional for this to be false | 41 |
| `@ConditionalOnMissingBean` | Back off if the user defined one | Put it on every starter bean | 41 |
| `@ConditionalOnBean` | Require another bean | Order-sensitive | 41 |
| `@ConditionalOnProperty` | Feature toggle | `matchIfMissing` for opt-out defaults | 41 |
| `@ConditionalOnWebApplication` | Servlet vs reactive | Batch apps share platform libraries | 41 |
| `@ImportRuntimeHints` | Native-image hints | Ship with the library | 29, 41 |
| `@RegisterReflectionForBinding` | Reflection hints for DTOs | For native images | 29 |

## C.3 AOP and cross-cutting

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@Aspect` + `@Around` / `@Before` | Define advice | Order aspects explicitly with `@Order` | 04 |
| `@EnableAsync` + `@Async` **(proxy)** | Run on an executor | Unbounded default queue; no transaction or security context | 25 |
| `@EnableScheduling` + `@Scheduled` | Scheduled jobs | Default pool of 1; set `zone`; one pod via ShedLock | 25 |
| `@SchedulerLock` (ShedLock) | Cluster-wide single execution | Not idempotency | 25 |
| `@EnableCaching` + `@Cacheable` **(proxy)** | Cache results | Explicit keys with every dimension | 21 |
| `@CachePut` / `@CacheEvict` **(proxy)** | Update / evict | Evict after commit | 21 |
| `@Retryable` (Spring Retry or Framework 7) **(proxy)** | Retry | Idempotent operations only; one retry layer | 26 |
| `@ConcurrencyLimit` (Framework 7) **(proxy)** | Semaphore bulkhead | Verify for your version | 26 |
| `@CircuitBreaker` / `@Retry` / `@Bulkhead` / `@RateLimiter` (Resilience4j) **(proxy)** | Resilience | Retry must wrap the breaker; ignore business exceptions | 26 |
| `@Observed` **(proxy)** | Metrics + span | Needs annotation support enabled | 27 |
| `@Timed` / `@Counted` **(proxy)** | Metrics | Low-cardinality tags only | 27 |
| `@Idempotent` (platform) **(proxy)** | Idempotency keys | Store key + result atomically | 04 |
| `@Audited` (platform) **(proxy)** | Audit trail | Record failures too; hashes, not values | 39 |

## C.4 Web (MVC and WebFlux)

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@RestController` | Controller with serialized responses | Return DTOs, not entities | 08 |
| `@RequestMapping` / `@GetMapping` / `@PostMapping`… | Map requests | Framework 7 adds a `version` attribute (verify) | 08, 20 |
| `@PathVariable` / `@RequestParam` | Bind path / query | Validate them (`@Validated` on the class) | 08, 09 |
| `@RequestBody` | Bind the body | `byte[]` for webhook signature verification | 18 |
| `@RequestHeader` | Bind a header | `If-Match`, `Idempotency-Key` | 08, 04 |
| `@ResponseStatus` | Fixed status | Prefer `ResponseEntity` for `Location`/ETag | 08 |
| `@RestControllerAdvice` + `@ExceptionHandler` | Central error handling | Doesn't see filter exceptions | 10 |
| `@CrossOrigin` | CORS per controller | Configure CORS through Security instead | 17 |
| `@HttpExchange` / `@GetExchange`… | Declarative HTTP clients | Build from Boot's `RestClient.Builder` | 19 |
| `@ImportHttpServices` (Boot 4) | Register HTTP interface groups | Verify for your version | 19 |
| `@Operation` / `@Tag` / `@Schema` (springdoc) | OpenAPI documentation | Reference the shared `Problem` schema | 20 |

## C.5 Validation

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@Valid` | Cascade validation | Needed on request bodies and nested objects | 09 |
| `@Validated` | Enable method validation; groups | On the class for parameter constraints | 09 |
| `@NotNull` / `@NotBlank` / `@NotEmpty` | Presence | `@NotBlank` for strings | 09 |
| `@Size` / `@Min` / `@Max` / `@Positive` | Bounds | Bound page sizes and batch sizes | 09, 20 |
| `@Pattern` / `@Email` | Format | Precompile in custom validators | 09 |
| `@Constraint` | Custom constraint | `@Pincode`, `@IndianMobile`, `@Gstin` | 09 |

## C.6 JSON (Jackson)

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@JsonProperty` | Rename a field | Renames are breaking changes | 11 |
| `@JsonIgnore` / `@JsonIgnoreProperties` | Exclude | Prefer separate DTOs | 11 |
| `@JsonInclude(NON_NULL)` | Omit nulls | Be consistent platform-wide | 11 |
| `@JsonFormat` | Date/number format | Prefer global ISO-8601 config | 11 |
| `@JsonValue` / `@JsonCreator` | Value-object serialization | For `Money`, ids | 11, 37 |
| `@JsonTypeInfo` / `@JsonSubTypes` | Polymorphism | Never default typing; allow-list subtypes | 11 |
| `@JsonComponent` (Boot 3) | Register serializers | Renamed in Boot 4 (verify) | 11 |

## C.7 Data and transactions

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@Transactional` **(proxy)** | Transaction boundary | Services only; no remote calls inside; checked exceptions don't roll back | 16 |
| `@Transactional(readOnly = true)` | Read-only hint | Enables optimizations; not a security control | 16 |
| `propagation = REQUIRES_NEW` | Independent transaction | Holds two connections | 16 |
| `propagation = MANDATORY` | Must run inside a transaction | Use for outbox writes | 36 |
| `@Entity` / `@Table` / `@Id` | JPA mapping | Keep entities out of the web layer | 13 |
| `@Version` | Optimistic locking | Source for ETags | 13, 16 |
| `@ManyToOne(fetch = LAZY)` | Relationships | Default `EAGER` on `@ManyToOne` — set LAZY | 13 |
| `@EntityGraph` | Fetch plan per query | N+1 fix | 13 |
| `@Query` | Custom JPQL/SQL | Native queries bypass Hibernate filters | 13, 38 |
| `@Modifying` | Update/delete queries | Clears nothing automatically — mind the persistence context | 13 |
| `@TenantId` (Hibernate 6+) | Discriminator tenancy | Doesn't cover native SQL — add RLS | 38 |
| `@Convert` / `@Converter` | Attribute conversion | Field encryption; encrypted columns aren't searchable | 39 |
| `@Document` / `@Indexed` (Mongo) | Document mapping | Create indexes via migrations | 22 |

## C.8 Security

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@EnableWebSecurity` / `@EnableWebFluxSecurity` | Security configuration | Define `SecurityFilterChain` beans | 17, 31 |
| `@EnableMethodSecurity` | Method security | Proxy rules apply | 17 |
| `@PreAuthorize` / `@PostAuthorize` **(proxy)** | Method authorization | Delegate complex rules to a bean | 17 |
| `@AuthenticationPrincipal` | Inject the principal | `Jwt` for resource servers | 18 |
| `@WithMockUser` / `@WithUserDetails` | Test security | Test anonymous, wrong role, wrong owner | 17 |

## C.9 Messaging

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@KafkaListener` | Consume Kafka | Idempotent handlers; concurrency ≤ partitions | 23 |
| `@RetryableTopic` + `@DltHandler` | Non-blocking retries | Loses ordering | 23 |
| `@RabbitListener` | Consume RabbitMQ | Don't requeue blindly | 24 |
| `@JmsListener` | Consume JMS | Idempotent by business key | 24 |
| `@PulsarListener` | Consume Pulsar | Choose the subscription type | 24 |
| `@MessageMapping` / `@SendToUser` | STOMP over WebSocket | Broker relay for multiple pods | 32 |
| `@ApplicationModuleListener` (Modulith) | Reliable module events | Monitor incomplete publications | 37 |

## C.10 GraphQL, gRPC, batch, AI

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@QueryMapping` / `@MutationMapping` | GraphQL root fields | Enforce ownership in resolvers | 32 |
| `@SchemaMapping` | Field resolver | N+1 across the network | 32 |
| `@BatchMapping` | Batched field resolver | Test call counts | 32 |
| `@GrpcService` | gRPC service | Starter-dependent import (verify) | 32 |
| `@StepScope` / `@JobScope` | Late-bound batch beans | Needed for job parameters in readers | 33 |
| `@Tool` / `@ToolParam` (Spring AI) | Expose a tool to a model | Identity from the session, never parameters | 40 |

## C.11 Actuator and observability

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@Endpoint(id)` + `@ReadOperation` | Custom Actuator endpoint | Secure it; management port | 27, 41 |
| `@Selector` | Path segment in an endpoint | e.g. `/actuator/platform/{code}` | 41 |
| `@WriteOperation` | Mutating endpoint | Audit it | 41 |

## C.12 Testing

| Annotation | Purpose | Pitfall | Ch |
|---|---|---|---|
| `@SpringBootTest` | Full context | Share contexts; avoid per-class variations | 15 |
| `@WebMvcTest` / `@WebFluxTest` | Web slice | Import your security config | 15, 17 |
| `@DataJpaTest` / `@JdbcTest` | Data slice | Use real PostgreSQL via Testcontainers | 15 |
| `@JsonTest` | JSON slice | Golden files | 11 |
| `@RestClientTest` | Client slice | `MockRestServiceServer` | 19 |
| `@GraphQlTest` | GraphQL slice | Assert batch counts | 32 |
| `@MockitoBean` / `@MockitoSpyBean` | Replace/spy beans | Replaces `@MockBean` (removed in Boot 4) | 15 |
| `@ServiceConnection` | Wire Testcontainers | Declare containers as shared beans | 15, 28 |
| `@DynamicPropertySource` | Dynamic properties | For services without connection details | 15 |
| `@TestConfiguration` | Test-only beans | Shared containers config | 15, 28 |
| `@SpringBatchTest` | Batch utilities | Test restart explicitly | 33 |
| `@ApplicationModuleTest` | Modulith module test | Bootstraps one module | 37 |
| `@AnalyzeClasses` + `@ArchTest` | ArchUnit rules | Freeze for legacy | 28, 37 |
| `@Tag` | Test groups | Separate nightly suites (ai-eval, e2e) | 28, 40 |

---

[:material-arrow-left: B Coding Exercises](b-coding-exercises.md) · [D Properties Cheat Sheet :material-arrow-right:](d-properties-cheat-sheet.md)
