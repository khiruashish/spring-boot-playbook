# Annotations Reference

Every annotation used across the handbook — **what it does, where it comes from, an example from the grocery platform, and the pitfall that matters** — plus a list of **outdated annotations and their replacements**.

!!! tip "Looking for something specific?"
    - **`@PathVariable` vs `@RequestParam`** → [Web Layer](web.md#pathvariable-vs-requestparam-the-one-everyone-asks-about)
    - **Upgrading old code** → [Outdated → Replacement](deprecated.md) (50 annotations with before/after examples)
    - **One-line lookup** → the [A–Z index](#az-index) below, or [Appendix C](../appendices/c-annotation-cheat-sheet.md) for the compact cheat sheet

## How the pages are organized

| Page | Covers |
|---|---|
| [Core Container](core-container.md) | Stereotypes, `@Bean`, injection, scopes, lifecycle, events, profiles, AOP |
| [Spring Boot](boot.md) | `@SpringBootApplication`, configuration properties, auto-configuration, conditions, native hints |
| [Web Layer](web.md) | Mappings, `@PathVariable` / `@RequestParam` and all binding annotations, responses, errors, HTTP clients |
| [Validation & JSON](validation-json.md) | `@Valid` / `@Validated`, Jakarta constraints, custom constraints, Jackson |
| [Data & Transactions](data.md) | JPA mapping, Hibernate extras, Spring Data queries, auditing, `@Transactional`, NoSQL |
| [Security](security.md) | Security configuration, method authorization, security testing |
| [Async, Messaging & Resilience](async-messaging.md) | `@Async`, `@Scheduled`, caching, Kafka, RabbitMQ, JMS, Pulsar, STOMP, GraphQL, Resilience4j, Framework 7 retry, Batch, Modulith, Spring AI |
| [Testing & Observability](testing-observability.md) | `@SpringBootTest`, slices, `@MockitoBean`, Testcontainers, JUnit, ArchUnit, metrics, tracing, Actuator |
| [Outdated → Replacement](deprecated.md) | Removed, deprecated, moved and superseded annotations |

## Legend

| Mark | Meaning |
|---|---|
| ✅ | Current and recommended |
| ⚠️ | Still works, but prefer the alternative described |
| ❌ | Removed or deprecated — see [Outdated → Replacement](deprecated.md) |
| 📦 | Same annotation, new package |
| 🧊 | Library in maintenance mode |
| **(proxy)** | Works only through a Spring proxy: public method, called from another bean — never self-invocation (Chapter 04) |
| **(verify)** | Boot 4 / Framework 7 detail still settling — confirm against your version's reference docs |

## Three things that explain most annotation surprises

1. **Proxies.** `@Transactional`, `@Cacheable`, `@Async`, `@Retryable`, `@PreAuthorize`, `@Validated`, `@Timed` and similar are applied by a proxy wrapped around your bean. A call from one method to another *in the same class* bypasses the proxy, so the annotation silently does nothing. Private methods are never proxied.
2. **Scanning.** Stereotype annotations only work for classes under the `@SpringBootApplication` package. A controller in a sibling package is never registered.
3. **Boot already did it.** `@EnableWebMvc`, `@EnableBatchProcessing` and some other `@Enable…` annotations don't just enable a feature in a Boot app — they *replace* Boot's auto-configuration with a manual one, switching off defaults you were relying on.

## A–Z index

### A

| Annotation | Area |
|---|---|
| [`@ActiveProfiles`](testing-observability.md) | Testing & Observability |
| [`@After`](core-container.md) | Core Container |
| [`@AfterAll`](testing-observability.md) | Testing & Observability |
| [`@AfterEach`](testing-observability.md) | Testing & Observability |
| [`@AfterReturning`](core-container.md) | Core Container |
| [`@AfterThrowing`](core-container.md) | Core Container |
| [`@AnalyzeClasses`](testing-observability.md) | Testing & Observability |
| [`@ApplicationModuleListener`](async-messaging.md) | Async, Messaging & Resilience |
| [`@ApplicationModuleTest`](testing-observability.md) | Testing & Observability |
| [`@ApplicationScope`](core-container.md) | Core Container |
| [`@ArchTest`](testing-observability.md) | Testing & Observability |
| [`@Argument`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Around`](core-container.md) | Core Container |
| [`@Aspect`](core-container.md) | Core Container |
| [`@AssertFalse`](validation-json.md) | Validation & JSON |
| [`@AssertTrue`](validation-json.md) | Validation & JSON |
| [`@Async`](async-messaging.md) | Async, Messaging & Resilience |
| [`@AttributeOverride`](data.md) | Data & Transactions |
| [`@AuthenticationPrincipal`](web.md) | Web Layer |
| [`@AutoConfiguration`](boot.md) | Spring Boot |
| [`@AutoConfigureAfter`](boot.md) | Spring Boot |
| [`@AutoConfigureBefore`](boot.md) | Spring Boot |
| [`@AutoConfigureMockMvc`](testing-observability.md) | Testing & Observability |
| [`@AutoConfigureOrder`](boot.md) | Spring Boot |
| [`@AutoConfigureTestDatabase`](testing-observability.md) | Testing & Observability |
| [`@AutoConfigureWebTestClient`](testing-observability.md) | Testing & Observability |
| [`@Autowired`](core-container.md) | Core Container |

### B

| Annotation | Area |
|---|---|
| [`@BatchMapping`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Bean`](core-container.md) | Core Container |
| [`@Before`](core-container.md) | Core Container |
| [`@BeforeAll`](testing-observability.md) | Testing & Observability |
| [`@BeforeEach`](testing-observability.md) | Testing & Observability |
| [`@Bulkhead`](async-messaging.md) | Async, Messaging & Resilience |

### C

| Annotation | Area |
|---|---|
| [`@Cacheable`](async-messaging.md) | Async, Messaging & Resilience |
| [`@CacheConfig`](async-messaging.md) | Async, Messaging & Resilience |
| [`@CacheEvict`](async-messaging.md) | Async, Messaging & Resilience |
| [`@CachePut`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Caching`](async-messaging.md) | Async, Messaging & Resilience |
| [`@CircuitBreaker`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Column`](data.md) | Data & Transactions |
| [`@Component`](core-container.md) | Core Container |
| [`@ComponentScan`](core-container.md) | Core Container |
| [`@ConcurrencyLimit`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Conditional`](core-container.md) | Core Container |
| [`@ConditionalOnBean`](boot.md) | Spring Boot |
| [`@ConditionalOnBooleanProperty`](boot.md) | Spring Boot |
| [`@ConditionalOnClass`](boot.md) | Spring Boot |
| [`@ConditionalOnCloudPlatform`](boot.md) | Spring Boot |
| [`@ConditionalOnExpression`](boot.md) | Spring Boot |
| [`@ConditionalOnJava`](boot.md) | Spring Boot |
| [`@ConditionalOnMissingBean`](boot.md) | Spring Boot |
| [`@ConditionalOnMissingClass`](boot.md) | Spring Boot |
| [`@ConditionalOnNotWebApplication`](boot.md) | Spring Boot |
| [`@ConditionalOnProperty`](boot.md) | Spring Boot |
| [`@ConditionalOnResource`](boot.md) | Spring Boot |
| [`@ConditionalOnSingleCandidate`](boot.md) | Spring Boot |
| [`@ConditionalOnThreading`](boot.md) | Spring Boot |
| [`@ConditionalOnWebApplication`](boot.md) | Spring Boot |
| [`@Configuration`](core-container.md) | Core Container |
| [`@ConfigurationProperties`](boot.md) | Spring Boot |
| [`@ConfigurationPropertiesScan`](boot.md) | Spring Boot |
| [`@Constraint`](validation-json.md) | Validation & JSON |
| [`@ConstructorBinding`](boot.md) | Spring Boot |
| [`@Container`](testing-observability.md) | Testing & Observability |
| [`@ContinueSpan`](testing-observability.md) | Testing & Observability |
| [`@Controller`](core-container.md) | Core Container |
| [`@ControllerAdvice`](web.md) | Web Layer |
| [`@Convert`](data.md) | Data & Transactions |
| [`@Converter`](data.md) | Data & Transactions |
| [`@CookieValue`](web.md) | Web Layer |
| [`@Counted`](testing-observability.md) | Testing & Observability |
| [`@CreatedBy`](data.md) | Data & Transactions |
| [`@CreatedDate`](data.md) | Data & Transactions |
| [`@CrossOrigin`](web.md) | Web Layer |
| [`@CsvSource`](testing-observability.md) | Testing & Observability |
| [`@CurrentSecurityContext`](security.md) | Security |

### D

| Annotation | Area |
|---|---|
| [`@DataJdbcTest`](testing-observability.md) | Testing & Observability |
| [`@DataJpaTest`](testing-observability.md) | Testing & Observability |
| [`@DataMongoTest`](testing-observability.md) | Testing & Observability |
| [`@DataRedisTest`](testing-observability.md) | Testing & Observability |
| [`@DataSizeUnit`](boot.md) | Spring Boot |
| [`@DecimalMax`](validation-json.md) | Validation & JSON |
| [`@DecimalMin`](validation-json.md) | Validation & JSON |
| [`@DefaultValue`](boot.md) | Spring Boot |
| [`@DeleteExchange`](web.md) | Web Layer |
| [`@DeleteMapping`](web.md) | Web Layer |
| [`@DeleteOperation`](testing-observability.md) | Testing & Observability |
| [`@DependsOn`](core-container.md) | Core Container |
| [`@DeprecatedConfigurationProperty`](boot.md) | Spring Boot |
| [`@Description`](core-container.md) | Core Container |
| [`@Digits`](validation-json.md) | Validation & JSON |
| [`@DirtiesContext`](testing-observability.md) | Testing & Observability |
| [`@Disabled`](testing-observability.md) | Testing & Observability |
| [`@DltHandler`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Document`](data.md) | Data & Transactions |
| [`@DurationUnit`](boot.md) | Spring Boot |
| [`@DynamicPropertySource`](testing-observability.md) | Testing & Observability |

### E

| Annotation | Area |
|---|---|
| [`@Email`](validation-json.md) | Validation & JSON |
| [`@Embeddable`](data.md) | Data & Transactions |
| [`@Embedded`](data.md) | Data & Transactions |
| [`@EnableAspectJAutoProxy`](core-container.md) | Core Container |
| [`@EnableAsync`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableAutoConfiguration`](boot.md) | Spring Boot |
| [`@EnableCaching`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableConfigurationProperties`](boot.md) | Spring Boot |
| [`@EnableJms`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableJpaAuditing`](data.md) | Data & Transactions |
| [`@EnableJpaRepositories`](data.md) | Data & Transactions |
| [`@EnableKafka`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableMethodSecurity`](security.md) | Security |
| [`@EnableMongoRepositories`](data.md) | Data & Transactions |
| [`@EnableRabbit`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableReactiveMethodSecurity`](security.md) | Security |
| [`@EnableRedisRepositories`](data.md) | Data & Transactions |
| [`@EnableResilientMethods`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableRetry`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableSchedulerLock`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableScheduling`](async-messaging.md) | Async, Messaging & Resilience |
| [`@EnableTransactionManagement`](data.md) | Data & Transactions |
| [`@EnableWebFluxSecurity`](security.md) | Security |
| [`@EnableWebSecurity`](security.md) | Security |
| [`@Endpoint`](testing-observability.md) | Testing & Observability |
| [`@EndpointWebExtension`](testing-observability.md) | Testing & Observability |
| [`@Entity`](data.md) | Data & Transactions |
| [`@EntityGraph`](data.md) | Data & Transactions |
| [`@EntityListeners`](data.md) | Data & Transactions |
| [`@Enumerated`](data.md) | Data & Transactions |
| [`@EventListener`](core-container.md) | Core Container |
| [`@ExceptionHandler`](web.md) | Web Layer |
| [`@ExtendWith`](testing-observability.md) | Testing & Observability |

### F

| Annotation | Area |
|---|---|
| [`@Field`](data.md) | Data & Transactions |
| [`@Future`](validation-json.md) | Validation & JSON |
| [`@FutureOrPresent`](validation-json.md) | Validation & JSON |

### G

| Annotation | Area |
|---|---|
| [`@GeneratedValue`](data.md) | Data & Transactions |
| [`@GetExchange`](web.md) | Web Layer |
| [`@GetMapping`](web.md) | Web Layer |
| [`@GraphQlTest`](testing-observability.md) | Testing & Observability |
| [`@GroupSequence`](validation-json.md) | Validation & JSON |
| [`@GrpcService`](async-messaging.md) | Async, Messaging & Resilience |

### H

| Annotation | Area |
|---|---|
| [`@Header`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Headers`](async-messaging.md) | Async, Messaging & Resilience |
| [`@HttpExchange`](web.md) | Web Layer |

### I

| Annotation | Area |
|---|---|
| [`@Id`](data.md) | Data & Transactions |
| [`@Import`](core-container.md) | Core Container |
| [`@ImportAutoConfiguration`](boot.md) | Spring Boot |
| [`@ImportHttpServices`](web.md) | Web Layer |
| [`@ImportRuntimeHints`](boot.md) | Spring Boot |
| [`@Indexed`](data.md) | Data & Transactions |
| [`@InitBinder`](web.md) | Web Layer |
| [`@Inject`](core-container.md) | Core Container |

### J

| Annotation | Area |
|---|---|
| [`@JacksonComponent`](validation-json.md) | Validation & JSON |
| [`@JacksonMixin`](validation-json.md) | Validation & JSON |
| [`@JdbcTest`](testing-observability.md) | Testing & Observability |
| [`@JdbcTypeCode`](data.md) | Data & Transactions |
| [`@JmsListener`](async-messaging.md) | Async, Messaging & Resilience |
| [`@JobScope`](async-messaging.md) | Async, Messaging & Resilience |
| [`@JoinColumn`](data.md) | Data & Transactions |
| [`@JsonAlias`](validation-json.md) | Validation & JSON |
| [`@JsonComponent`](validation-json.md) | Validation & JSON |
| [`@JsonCreator`](validation-json.md) | Validation & JSON |
| [`@JsonFormat`](validation-json.md) | Validation & JSON |
| [`@JsonIgnore`](validation-json.md) | Validation & JSON |
| [`@JsonIgnoreProperties`](validation-json.md) | Validation & JSON |
| [`@JsonInclude`](validation-json.md) | Validation & JSON |
| [`@JsonMixin`](validation-json.md) | Validation & JSON |
| [`@JsonNaming`](validation-json.md) | Validation & JSON |
| [`@JsonProperty`](validation-json.md) | Validation & JSON |
| [`@JsonPropertyOrder`](validation-json.md) | Validation & JSON |
| [`@JsonSubTypes`](validation-json.md) | Validation & JSON |
| [`@JsonTest`](testing-observability.md) | Testing & Observability |
| [`@JsonTypeInfo`](validation-json.md) | Validation & JSON |
| [`@JsonUnwrapped`](validation-json.md) | Validation & JSON |
| [`@JsonValue`](validation-json.md) | Validation & JSON |
| [`@JsonView`](validation-json.md) | Validation & JSON |

### K

| Annotation | Area |
|---|---|
| [`@KafkaListener`](async-messaging.md) | Async, Messaging & Resilience |

### L

| Annotation | Area |
|---|---|
| [`@LastModifiedBy`](data.md) | Data & Transactions |
| [`@LastModifiedDate`](data.md) | Data & Transactions |
| [`@Lazy`](core-container.md) | Core Container |
| [`@Lob`](data.md) | Data & Transactions |
| [`@LocalServerPort`](testing-observability.md) | Testing & Observability |
| [`@Lock`](data.md) | Data & Transactions |
| [`@Lookup`](core-container.md) | Core Container |

### M

| Annotation | Area |
|---|---|
| [`@ManyToMany`](data.md) | Data & Transactions |
| [`@ManyToOne`](data.md) | Data & Transactions |
| [`@MappedSuperclass`](data.md) | Data & Transactions |
| [`@MatrixVariable`](web.md) | Web Layer |
| [`@Max`](validation-json.md) | Validation & JSON |
| [`@MessageMapping`](async-messaging.md) | Async, Messaging & Resilience |
| [`@MethodSource`](testing-observability.md) | Testing & Observability |
| [`@Min`](validation-json.md) | Validation & JSON |
| [`@MockitoBean`](testing-observability.md) | Testing & Observability |
| [`@MockitoSpyBean`](testing-observability.md) | Testing & Observability |
| [`@ModelAttribute`](web.md) | Web Layer |
| [`@Modifying`](data.md) | Data & Transactions |
| [`@MutationMapping`](async-messaging.md) | Async, Messaging & Resilience |

### N

| Annotation | Area |
|---|---|
| [`@Name`](boot.md) | Spring Boot |
| [`@Named`](core-container.md) | Core Container |
| [`@NativeQuery`](data.md) | Data & Transactions |
| [`@Negative`](validation-json.md) | Validation & JSON |
| [`@NegativeOrZero`](validation-json.md) | Validation & JSON |
| [`@Nested`](testing-observability.md) | Testing & Observability |
| [`@NestedConfigurationProperty`](boot.md) | Spring Boot |
| [`@NewSpan`](testing-observability.md) | Testing & Observability |
| [`@NotBlank`](validation-json.md) | Validation & JSON |
| [`@NotEmpty`](validation-json.md) | Validation & JSON |
| [`@NotNull`](validation-json.md) | Validation & JSON |
| [`@Null`](validation-json.md) | Validation & JSON |

### O

| Annotation | Area |
|---|---|
| [`@Observed`](testing-observability.md) | Testing & Observability |
| [`@OneToMany`](data.md) | Data & Transactions |
| [`@OneToOne`](data.md) | Data & Transactions |
| [`@Order`](core-container.md) | Core Container |

### P

| Annotation | Area |
|---|---|
| [`@Param`](data.md) | Data & Transactions |
| [`@ParameterizedTest`](testing-observability.md) | Testing & Observability |
| [`@Past`](validation-json.md) | Validation & JSON |
| [`@PastOrPresent`](validation-json.md) | Validation & JSON |
| [`@PatchExchange`](web.md) | Web Layer |
| [`@PatchMapping`](web.md) | Web Layer |
| [`@PathVariable`](web.md) | Web Layer |
| [`@Pattern`](validation-json.md) | Validation & JSON |
| [`@Payload`](async-messaging.md) | Async, Messaging & Resilience |
| [`@PeriodUnit`](boot.md) | Spring Boot |
| [`@Pincode`](validation-json.md) | Validation & JSON |
| [`@Pointcut`](core-container.md) | Core Container |
| [`@Positive`](validation-json.md) | Validation & JSON |
| [`@PositiveOrZero`](validation-json.md) | Validation & JSON |
| [`@PostAuthorize`](security.md) | Security |
| [`@PostConstruct`](core-container.md) | Core Container |
| [`@PostExchange`](web.md) | Web Layer |
| [`@PostFilter`](security.md) | Security |
| [`@PostLoad`](data.md) | Data & Transactions |
| [`@PostMapping`](web.md) | Web Layer |
| [`@PreAuthorize`](security.md) | Security |
| [`@PreDestroy`](core-container.md) | Core Container |
| [`@PreFilter`](security.md) | Security |
| [`@PrePersist`](data.md) | Data & Transactions |
| [`@PreUpdate`](data.md) | Data & Transactions |
| [`@Primary`](core-container.md) | Core Container |
| [`@Procedure`](data.md) | Data & Transactions |
| [`@Profile`](core-container.md) | Core Container |
| [`@PulsarListener`](async-messaging.md) | Async, Messaging & Resilience |
| [`@PutExchange`](web.md) | Web Layer |
| [`@PutMapping`](web.md) | Web Layer |

### Q

| Annotation | Area |
|---|---|
| [`@Qualifier`](core-container.md) | Core Container |
| [`@Query`](data.md) | Data & Transactions |
| [`@QueryHints`](data.md) | Data & Transactions |
| [`@QueryMapping`](async-messaging.md) | Async, Messaging & Resilience |

### R

| Annotation | Area |
|---|---|
| [`@RabbitHandler`](async-messaging.md) | Async, Messaging & Resilience |
| [`@RabbitListener`](async-messaging.md) | Async, Messaging & Resilience |
| [`@RateLimiter`](async-messaging.md) | Async, Messaging & Resilience |
| [`@ReadOperation`](testing-observability.md) | Testing & Observability |
| [`@Recover`](async-messaging.md) | Async, Messaging & Resilience |
| [`@RedisHash`](data.md) | Data & Transactions |
| [`@Reflective`](boot.md) | Spring Boot |
| [`@RegisterReflectionForBinding`](boot.md) | Spring Boot |
| [`@Repository`](core-container.md) | Core Container |
| [`@RequestAttribute`](web.md) | Web Layer |
| [`@RequestBody`](web.md) | Web Layer |
| [`@RequestHeader`](web.md) | Web Layer |
| [`@RequestMapping`](web.md) | Web Layer |
| [`@RequestParam`](web.md) | Web Layer |
| [`@RequestPart`](web.md) | Web Layer |
| [`@RequestScope`](core-container.md) | Core Container |
| [`@ResponseBody`](web.md) | Web Layer |
| [`@ResponseStatus`](web.md) | Web Layer |
| [`@RestClientTest`](testing-observability.md) | Testing & Observability |
| [`@RestController`](web.md) | Web Layer |
| [`@RestControllerAdvice`](web.md) | Web Layer |
| [`@Retry`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Retryable`](async-messaging.md) | Async, Messaging & Resilience |
| [`@RetryableTopic`](async-messaging.md) | Async, Messaging & Resilience |
| [`@RolesAllowed`](security.md) | Security |

### S

| Annotation | Area |
|---|---|
| [`@Scheduled`](async-messaging.md) | Async, Messaging & Resilience |
| [`@SchedulerLock`](async-messaging.md) | Async, Messaging & Resilience |
| [`@SchemaMapping`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Scope`](core-container.md) | Core Container |
| [`@Secured`](security.md) | Security |
| [`@Selector`](testing-observability.md) | Testing & Observability |
| [`@SendTo`](async-messaging.md) | Async, Messaging & Resilience |
| [`@SendToUser`](async-messaging.md) | Async, Messaging & Resilience |
| [`@SequenceGenerator`](data.md) | Data & Transactions |
| [`@Service`](core-container.md) | Core Container |
| [`@ServiceConnection`](testing-observability.md) | Testing & Observability |
| [`@ServletComponentScan`](boot.md) | Spring Boot |
| [`@SessionAttribute`](web.md) | Web Layer |
| [`@SessionScope`](core-container.md) | Core Container |
| [`@Size`](validation-json.md) | Validation & JSON |
| [`@SpanTag`](testing-observability.md) | Testing & Observability |
| [`@SpringBatchTest`](testing-observability.md) | Testing & Observability |
| [`@SpringBootApplication`](boot.md) | Spring Boot |
| [`@SpringBootConfiguration`](boot.md) | Spring Boot |
| [`@SpringBootTest`](testing-observability.md) | Testing & Observability |
| [`@Sql`](testing-observability.md) | Testing & Observability |
| [`@SqlGroup`](testing-observability.md) | Testing & Observability |
| [`@SQLRestriction`](data.md) | Data & Transactions |
| [`@StepScope`](async-messaging.md) | Async, Messaging & Resilience |
| [`@SubscribeMapping`](async-messaging.md) | Async, Messaging & Resilience |
| [`@SubscriptionMapping`](async-messaging.md) | Async, Messaging & Resilience |

### T

| Annotation | Area |
|---|---|
| [`@Table`](data.md) | Data & Transactions |
| [`@Tag`](testing-observability.md) | Testing & Observability |
| [`@TenantId`](data.md) | Data & Transactions |
| [`@Test`](testing-observability.md) | Testing & Observability |
| [`@TestBean`](testing-observability.md) | Testing & Observability |
| [`@TestConfiguration`](testing-observability.md) | Testing & Observability |
| [`@Testcontainers`](testing-observability.md) | Testing & Observability |
| [`@TestFactory`](testing-observability.md) | Testing & Observability |
| [`@TestPropertySource`](testing-observability.md) | Testing & Observability |
| [`@Timed`](testing-observability.md) | Testing & Observability |
| [`@TimeLimiter`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Timeout`](testing-observability.md) | Testing & Observability |
| [`@TimeToLive`](data.md) | Data & Transactions |
| [`@Tool`](async-messaging.md) | Async, Messaging & Resilience |
| [`@ToolParam`](async-messaging.md) | Async, Messaging & Resilience |
| [`@Transactional`](data.md) | Data & Transactions |
| [`@TransactionalEventListener`](core-container.md) | Core Container |
| [`@Transient`](data.md) | Data & Transactions |

### U

| Annotation | Area |
|---|---|
| [`@UuidGenerator`](data.md) | Data & Transactions |

### V

| Annotation | Area |
|---|---|
| [`@Valid`](validation-json.md) | Validation & JSON |
| [`@Validated`](validation-json.md) | Validation & JSON |
| [`@Value`](core-container.md) | Core Container |
| [`@ValueSource`](testing-observability.md) | Testing & Observability |
| [`@Version`](data.md) | Data & Transactions |

### W

| Annotation | Area |
|---|---|
| [`@WebEndpoint`](testing-observability.md) | Testing & Observability |
| [`@WebFluxTest`](testing-observability.md) | Testing & Observability |
| [`@WebMvcTest`](testing-observability.md) | Testing & Observability |
| [`@WithAnonymousUser`](security.md) | Security |
| [`@WithMockUser`](security.md) | Security |
| [`@WithSecurityContext`](security.md) | Security |
| [`@WithUserDetails`](security.md) | Security |
| [`@WriteOperation`](testing-observability.md) | Testing & Observability |

---

[Core Container :material-arrow-right:](core-container.md)
