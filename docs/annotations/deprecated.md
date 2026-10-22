# Outdated Annotations → Replacements

Annotations (and the annotation-driven patterns around them) that are **removed**, **deprecated**, **moved**, or **superseded by a better practice**, with what to use instead. Use this page when reading older code, answering "why doesn't this compile after the upgrade?", or reviewing a legacy service before migration (Chapter 42).

| Status | Meaning |
|---|---|
| ❌ **Removed** | No longer exists in the current version — code won't compile |
| ⚠️ **Deprecated** | Still works, scheduled for removal — replace now |
| 📦 **Moved** | Same annotation, new package — change the import |
| 🔄 **Superseded** | Not deprecated, but a newer approach is the recommended default |
| 🧊 **Maintenance** | Library still works but receives no new features |

!!! warning "Verify version-specific rows"
    Rows marked **(verify)** involve Boot 4, Framework 7, Security 7 or Hibernate 7 changes that were still settling when this was written. Confirm against the migration guide for your exact versions. Everything else reflects long-established changes.

## Quick migration table

| # | Outdated | Replacement | Status | Changed in | Ch |
|---|---|---|---|---|---|
| 1 | `javax.annotation.PostConstruct` / `@PreDestroy` | `jakarta.annotation.PostConstruct` / `@PreDestroy` | 📦 | Boot 3 (Jakarta EE 9+) | 03 |
| 2 | `javax.persistence.*` (`@Entity`, `@Id`, `@Column`…) | `jakarta.persistence.*` | 📦 | Boot 3 | 13 |
| 3 | `javax.validation.*` (`@NotNull`, `@Valid`…) | `jakarta.validation.*` | 📦 | Boot 3 | 09 |
| 4 | `javax.inject.Inject` / `@Named` | `jakarta.inject.*` — or plain constructor injection | 📦 | Boot 3 | 02 |
| 5 | `javax.transaction.Transactional` | Spring's `org.springframework.transaction.annotation.Transactional` | 📦/🔄 | Boot 3 | 16 |
| 6 | `@MockBean` / `@SpyBean` | `@MockitoBean` / `@MockitoSpyBean` | ⚠️ in 3.4 → ❌ in 4.0 | Boot 3.4 / 4.0 | 15 |
| 7 | `@MockBeans` / `@SpyBeans` (containers) | Repeat `@MockitoBean` fields | ❌ | Boot 4.0 | 15 |
| 8 | `@RunWith(SpringRunner.class)` (JUnit 4) | Nothing — `@SpringBootTest` and slices include `@ExtendWith(SpringExtension.class)` | ❌ (vintage engine dropped from starter) | Boot 2.4 | 15 |
| 9 | JUnit 4 `@Test`, `@Before`, `@After`, `@BeforeClass` | JUnit Jupiter `@Test`, `@BeforeEach`, `@AfterEach`, `@BeforeAll` | 🔄 | Boot 2.2+ | 15 |
| 10 | `@RunWith(MockitoJUnitRunner.class)` | `@ExtendWith(MockitoExtension.class)` | 🔄 | JUnit 5 | 15 |
| 11 | `org.springframework.boot.web.server.LocalServerPort` | `org.springframework.boot.test.web.server.LocalServerPort` | 📦 | Boot 2.7 → old removed 3.0 | 15 |
| 12 | `@ConstructorBinding` on the class (Boot 2.x) | Not needed for a single constructor; for several, `@ConstructorBinding` from `...context.properties.bind` on the constructor | 📦/🔄 | Boot 3.0 | 06 |
| 13 | `@ConfigurationProperties` with setters/`@Data` classes | Immutable **records** with constructor binding | 🔄 | Boot 2.6+ (records) | 06 |
| 14 | `@Required` (setter injection) | Constructor injection | ❌ | Framework 6.0 | 02 |
| 15 | `@Autowired` on fields | Constructor injection (`@Autowired` optional on a single constructor) | 🔄 | Framework 4.3+ | 02 |
| 16 | `org.springframework.lang.@Nullable` / `@NonNull` / `@NonNullApi` | JSpecify `@Nullable` / `@NullMarked` | ⚠️ (verify) | Framework 7 / Boot 4 | 42 |
| 17 | `@EnableGlobalMethodSecurity(prePostEnabled = true)` | `@EnableMethodSecurity` (pre/post enabled by default) | ⚠️ → ❌ (verify removal) | Security 5.6 / 6.x / 7 | 17 |
| 18 | `@EnableWebSecurity` + `WebSecurityConfigurerAdapter` subclass | `@EnableWebSecurity` (optional in Boot) + `SecurityFilterChain` bean | ❌ (adapter) | Security 5.7 deprecated / 6.0 removed | 17 |
| 19 | `@EnableResourceServer`, `@EnableAuthorizationServer`, `@EnableOAuth2Sso` (spring-security-oauth2) | `oauth2ResourceServer()`, **Spring Authorization Server**, `oauth2Login()` | ❌ (project end-of-life) | Spring Security 5.x era | 18 |
| 20 | `@EnableEurekaClient` | Nothing — having the client on the classpath registers it; `@EnableDiscoveryClient` optional | ❌ | Spring Cloud 2022.0 | 35 |
| 21 | `@EnableHystrix`, `@EnableCircuitBreaker`, `@HystrixCommand` | Resilience4j `@CircuitBreaker`, `@Retry`, `@Bulkhead`, `@TimeLimiter` | ❌ | Spring Cloud 2020.0 | 26 |
| 22 | `@EnableZuulProxy` | **Spring Cloud Gateway** routes | ❌ | Spring Cloud 2020.0 | 35 |
| 23 | `@RibbonClient` | `@LoadBalancerClient` (Spring Cloud LoadBalancer) — or Kubernetes DNS | ❌ | Spring Cloud 2020.0 | 35 |
| 24 | `@EnableFeignClients` / `@FeignClient` | `@HttpExchange` interfaces backed by `RestClient` | 🧊 | Spring Cloud OpenFeign in maintenance | 19 |
| 25 | Sleuth `@NewSpan`, `@ContinueSpan`, `@SpanTag` | Micrometer Tracing equivalents (`io.micrometer.tracing.annotation`) or `@Observed` | ❌ (Sleuth) / 📦 | Boot 3.0 | 27 |
| 26 | Spring Cloud Stream `@EnableBinding`, `@StreamListener`, `@Input`, `@Output`, `@SendTo` (stream) | Functional beans: `Supplier`, `Function`, `Consumer` + `spring.cloud.function.definition` | ❌ | Spring Cloud Stream 4.0 | 24 |
| 27 | Springfox `@Api`, `@ApiOperation`, `@ApiParam`, `@ApiModel` | springdoc / OpenAPI 3 `@Tag`, `@Operation`, `@Parameter`, `@Schema` | ❌ (Springfox unmaintained, incompatible with Boot 3) | Boot 3 | 20 |
| 28 | `@JsonComponent` (Boot) | `@JacksonComponent` (verify) | 📦 (verify) | Boot 4 / Jackson 3 | 11 |
| 29 | `@JsonMixin` (Boot) | `@JacksonMixin` (verify) | 📦 (verify) | Boot 4 | 11 |
| 30 | Jackson 2 databind types next to annotations (`com.fasterxml.jackson.databind.annotation.*`) | Jackson 3: core annotations stay in `com.fasterxml.jackson.annotation`; databind annotations move to `tools.jackson.databind.annotation` | 📦 partial (verify) | Jackson 3 / Boot 4 | 11 |
| 31 | Hibernate `@Type(type = "...")`, `@TypeDef`, `@TypeDefs` | `@JdbcTypeCode(SqlTypes.JSON)`, `@Type(MyUserType.class)`, `@Convert` | ❌ | Hibernate 6 / Boot 3 | 13 |
| 32 | Hibernate `@Where` | `@SQLRestriction` | ⚠️ | Hibernate 6.3 | 13 |
| 33 | Hibernate `@Loader` | `@SQLSelect` / named queries | ⚠️ (verify) | Hibernate 6.x | 13 |
| 34 | Hibernate `@GenericGenerator` | `@UuidGenerator`, `@SequenceGenerator`, or `@IdGeneratorType` custom annotations | ⚠️ (verify) | Hibernate 6.5 | 13 |
| 35 | Spring Retry `@Retryable`, `@Recover`, `@EnableRetry` | Framework 7 `@Retryable` + `@EnableResilientMethods` for simple cases; Resilience4j for breakers | 🧊/🔄 (verify) | Framework 7 | 26 |
| 36 | `@EnableBatchProcessing` in a Boot app | Omit it — Boot auto-configures batch; adding it **disables** that auto-configuration | 🔄 | Batch 5 / Boot 3 | 33 |
| 37 | `JobBuilderFactory` / `StepBuilderFactory` injection | `new JobBuilder(name, jobRepository)` / `new StepBuilder(name, jobRepository)` | ❌ | Batch 5 / Boot 3 | 33 |
| 38 | `@EnableKafka`, `@EnableRabbit`, `@EnableTransactionManagement`, `@EnableJpaRepositories` in plain Boot apps | Omit — auto-configured | 🔄 | Boot 1.x+ | 05 |
| 39 | `@EnableWebMvc` in a Boot app | Omit, and customize via `WebMvcConfigurer` — the annotation **turns off** Boot's MVC auto-configuration | 🔄 | Boot 1.x+ | 08 |
| 40 | `@RequestMapping(method = RequestMethod.GET)` on methods | `@GetMapping` and the other composed mappings | 🔄 | Framework 4.3 | 08 |
| 41 | `@Controller` + `@ResponseBody` on every method | `@RestController` | 🔄 | Framework 4.0 | 08 |
| 42 | `@ResponseStatus` on custom exceptions as the error strategy | `@RestControllerAdvice` returning `ProblemDetail` (RFC 9457) | 🔄 | Framework 6 / Boot 3 | 10 |
| 43 | Web-test slice imports `org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest` etc. | Technology-specific test modules and packages | 📦 (verify) | Boot 4 | 15, 42 |
| 44 | Hand-rolled API version paths only | `version` attribute on `@RequestMapping` + `ApiVersionConfigurer` | 🔄 (verify) | Framework 7 | 20 |
| 45 | `RestTemplate` beans wired with `@LoadBalanced` | `RestClient.Builder` (still `@LoadBalanced`-capable) or Kubernetes DNS | 🧊 | Framework 6.1 | 19 |
| 46 | Legacy `@EnableScheduling` jobs without cluster locking | Keep `@Scheduled`, add ShedLock `@SchedulerLock` or run a Kubernetes CronJob | 🔄 | — | 25 |
| 47 | `@Async` on the unbounded default executor | `@Async("namedExecutor")` with a bounded queue | 🔄 | — | 25 |
| 48 | `@AutoConfigureTestDatabase` default (replaces your DB with an embedded one) | `@AutoConfigureTestDatabase(replace = NONE)` with Testcontainers + `@ServiceConnection` | 🔄 | Boot 3.1+ | 15, 28 |
| 49 | Lombok `@Data` / `@Setter` on DTOs and `@ConfigurationProperties` | Java records | 🔄 | Java 16+ | 01, 06 |
| 50 | `@Value("${...}")` scattered across classes | `@ConfigurationProperties` records with `@Validated` | 🔄 | — | 06 |

---

## Before and after, for the ones you'll hit most

### 1–5 · `javax.*` → `jakarta.*` (Boot 3)

=== "Before (Boot 2.x)"

    ```java title="OrderEntity.java"
    import javax.annotation.PostConstruct;
    import javax.persistence.Entity;
    import javax.persistence.Id;
    import javax.validation.constraints.NotBlank;

    @Entity
    public class OrderEntity {
        @Id private Long id;
        @NotBlank private String orderRef;
    }
    ```

=== "After (Boot 3/4)"

    ```java title="OrderEntity.java"
    import jakarta.annotation.PostConstruct;
    import jakarta.persistence.Entity;
    import jakarta.persistence.Id;
    import jakarta.validation.constraints.NotBlank;

    @Entity
    public class OrderEntity {
        @Id private Long id;
        @NotBlank private String orderRef;
    }
    ```

Automated by OpenRewrite (`org.openrewrite.java.migrate.jakarta.JavaxMigrationToJakarta`, included in the Boot 3 upgrade recipe). Third-party libraries must also ship Jakarta versions.

### 6–7 · `@MockBean` → `@MockitoBean`

=== "Before (Boot ≤ 3.3)"

    ```java title="CartControllerTest.java"
    import org.springframework.boot.test.mock.mockito.MockBean;

    @WebMvcTest(CartController.class)
    class CartControllerTest {
        @MockBean CartDelegate delegate;
    }
    ```

=== "After (Boot 3.4+ / required in 4)"

    ```java title="CartControllerTest.java"
    import org.springframework.test.context.bean.override.mockito.MockitoBean;

    @WebMvcTest(CartController.class)
    class CartControllerTest {
        @MockitoBean CartDelegate delegate;
    }
    ```

The replacement lives in **Spring Framework** (`spring-test`), not Boot. Note that it cannot be placed on a `@Configuration` class, only on test class fields.

### 8–10 · JUnit 4 runners → JUnit 5 extensions

=== "Before"

    ```java title="OrderServiceTest.java"
    @RunWith(SpringRunner.class)
    @SpringBootTest
    public class OrderServiceTest {
        @Before public void setUp() { ... }
        @Test public void placesOrder() { ... }
    }
    ```

=== "After"

    ```java title="OrderServiceTest.java"
    @SpringBootTest                       // already includes @ExtendWith(SpringExtension.class)
    class OrderServiceTest {
        @BeforeEach void setUp() { ... }
        @Test void placesOrder() { ... }   // org.junit.jupiter.api.Test
    }
    ```

### 12–13 · `@ConstructorBinding` and records

=== "Before (Boot 2.x)"

    ```java title="CartProperties.java"
    @ConstructorBinding                              // org.springframework.boot.context.properties
    @ConfigurationProperties("grocery.cart")
    public class CartProperties {
        private final int maxLines;
        public CartProperties(int maxLines) { this.maxLines = maxLines; }
        public int getMaxLines() { return maxLines; }
    }
    ```

=== "After (Boot 3/4)"

    ```java title="CartProperties.java"
    @ConfigurationProperties("grocery.cart")
    @Validated
    public record CartProperties(@DefaultValue("50") @Min(1) int maxLines) {}   // no @ConstructorBinding needed
    ```

### 15 · Field injection → constructor injection

=== "Before"

    ```java title="OrderService.java"
    @Service
    public class OrderService {
        @Autowired private OrderRepository orders;          // hidden dependency, hard to test
        @Autowired private PricingClient pricing;
    }
    ```

=== "After"

    ```java title="OrderService.java"
    @Service
    public class OrderService {
        private final OrderRepository orders;
        private final PricingClient pricing;

        public OrderService(OrderRepository orders, PricingClient pricing) {   // @Autowired optional
            this.orders = orders;
            this.pricing = pricing;
        }
    }
    ```

### 17–18 · Method and web security configuration

=== "Before (Security 5.x)"

    ```java title="SecurityConfig.java"
    @EnableWebSecurity
    @EnableGlobalMethodSecurity(prePostEnabled = true)
    public class SecurityConfig extends WebSecurityConfigurerAdapter {
        @Override
        protected void configure(HttpSecurity http) throws Exception {
            http.authorizeRequests().antMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated();
        }
    }
    ```

=== "After (Security 6/7)"

    ```java title="SecurityConfig.java"
    @Configuration(proxyBeanMethods = false)
    @EnableMethodSecurity
    class SecurityConfig {
        @Bean
        SecurityFilterChain api(HttpSecurity http) throws Exception {
            return http
                    .authorizeHttpRequests(a -> a
                            .requestMatchers("/api/public/**").permitAll()
                            .anyRequest().authenticated())
                    .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
                    .build();
        }
    }
    ```

Note the related non-annotation changes: `authorizeRequests` → `authorizeHttpRequests`, `antMatchers` → `requestMatchers`, and in Security 7 the lambda DSL only.

### 21 · Hystrix → Resilience4j

=== "Before"

    ```java title="PricingGateway.java"
    @HystrixCommand(fallbackMethod = "cachedPrice",
            commandProperties = @HystrixProperty(name = "execution.isolation.thread.timeoutInMilliseconds", value = "600"))
    public PriceView price(String sku, String pincode) { ... }
    ```

=== "After"

    ```java title="PricingGateway.java"
    @CircuitBreaker(name = "pricing", fallbackMethod = "cachedPrice")   // timeout on the HTTP client (Ch 19)
    @Retry(name = "pricing")
    public PriceView price(String sku, String pincode) { ... }
    ```

### 24 · Feign → HTTP interface

=== "Before"

    ```java title="PricingClient.java"
    @FeignClient(name = "pricing-service", url = "${grocery.pricing.url}")
    public interface PricingClient {
        @GetMapping("/api/v1/prices/{sku}")
        PriceResponse price(@PathVariable("sku") String sku, @RequestParam("pincode") String pincode);
    }
    ```

=== "After"

    ```java title="PricingApi.java"
    @HttpExchange("/api/v1/prices")
    public interface PricingApi {
        @GetExchange("/{sku}")
        PriceResponse price(@PathVariable String sku, @RequestParam String pincode);
    }
    ```

### 26 · Spring Cloud Stream annotations → functions

=== "Before"

    ```java title="OrderEventsListener.java"
    @EnableBinding(Sink.class)
    public class OrderEventsListener {
        @StreamListener(Sink.INPUT)
        public void handle(OrderPlaced event) { ... }
    }
    ```

=== "After"

    ```java title="OrderEventsConfig.java"
    @Bean
    Consumer<OrderPlaced> handleOrderPlaced(NotificationService notifications) {
        return notifications::orderPlaced;         // spring.cloud.function.definition=handleOrderPlaced
    }
    ```

### 27 · Springfox → springdoc

=== "Before"

    ```java title="CartController.java"
    @Api(tags = "Cart")
    @ApiOperation("Add an item to the cart")
    @PostMapping("/{cartId}/items")
    public CartView add(@ApiParam("Cart id") @PathVariable UUID cartId, ...) { ... }
    ```

=== "After"

    ```java title="CartController.java"
    @Tag(name = "Cart")
    @Operation(summary = "Add an item to the cart")
    @PostMapping("/{cartId}/items")
    public CartView add(@Parameter(description = "Cart id") @PathVariable UUID cartId, ...) { ... }
    ```

### 31–32 · Hibernate type and filter annotations

=== "Before (Hibernate 5)"

    ```java title="ProductEntity.java"
    @TypeDef(name = "jsonb", typeClass = JsonBinaryType.class)
    @Where(clause = "deleted = false")
    @Entity
    public class ProductEntity {
        @Type(type = "jsonb")
        @Column(columnDefinition = "jsonb")
        private Map<String, Object> attributes;
    }
    ```

=== "After (Hibernate 6/7)"

    ```java title="ProductEntity.java"
    @SQLRestriction("deleted = false")
    @Entity
    public class ProductEntity {
        @JdbcTypeCode(SqlTypes.JSON)
        private Map<String, Object> attributes;
    }
    ```

### 35 · Spring Retry → Framework 7 core retry (verify)

=== "Before (Spring Retry)"

    ```java title="InventoryGateway.java"
    @EnableRetry
    @Configuration
    class RetryConfig {}

    @Retryable(retryFor = DependencyException.class, maxAttempts = 3, backoff = @Backoff(delay = 100, multiplier = 2))
    public StockView stock(String sku) { ... }
    ```

=== "After (Framework 7)"

    ```java title="InventoryGateway.java"
    @EnableResilientMethods
    @Configuration(proxyBeanMethods = false)
    class ResilienceConfig {}

    @Retryable(includes = DependencyException.class, maxRetries = 2, delay = 100, multiplier = 2)
    public StockView stock(String sku) { ... }
    ```

Note the attribute semantics: `maxAttempts = 3` (total) corresponds to `maxRetries = 2` (additional). **Verify** names in the Framework 7 reference.

### 36–37 · Spring Batch configuration

=== "Before (Batch 4)"

    ```java title="SettlementJobConfig.java"
    @EnableBatchProcessing
    @Configuration
    public class SettlementJobConfig {
        @Autowired JobBuilderFactory jobs;
        @Autowired StepBuilderFactory steps;

        @Bean Job job() { return jobs.get("sellerSettlementJob").start(step()).build(); }
    }
    ```

=== "After (Batch 5+)"

    ```java title="SettlementJobConfig.java"
    @Configuration(proxyBeanMethods = false)          // no @EnableBatchProcessing in Boot apps
    class SettlementJobConfig {
        @Bean
        Job sellerSettlementJob(JobRepository repository, Step calculateStep) {
            return new JobBuilder("sellerSettlementJob", repository).start(calculateStep).build();
        }
    }
    ```

---

## Finding outdated annotations in a codebase

```bash title="Terminal"
# javax imports that should be jakarta
grep -rn "import javax\.\(persistence\|validation\|annotation\.\(PostConstruct\|PreDestroy\)\|inject\|servlet\|transaction\)" src/

# removed or deprecated test annotations
grep -rn "@MockBean\|@SpyBean\|@RunWith\|org.junit.Test" src/test/

# legacy Spring Cloud / security / docs annotations
grep -rn "@EnableHystrix\|@HystrixCommand\|@EnableZuulProxy\|@RibbonClient\|@EnableEurekaClient\|@EnableGlobalMethodSecurity\|WebSecurityConfigurerAdapter\|@EnableBinding\|@StreamListener\|@ApiOperation" src/

# style-level: field injection and @Value sprawl
grep -rn "@Autowired$" -A1 src/main | grep "private"
grep -rc "@Value(\"\${" src/main | grep -v ":0"
```

Most of these are fixed automatically by OpenRewrite recipes (Chapter 42): the Spring Boot upgrade recipes, `JavaxMigrationToJakarta`, the Spring Security migration recipes, and the JUnit 4 → 5 recipe. Run `rewriteDryRun`, review the patch, then fix what remains by hand.

---

[:material-arrow-left: Testing & Observability](testing-observability.md) · [Annotations Home :material-arrow-right:](index.md)
