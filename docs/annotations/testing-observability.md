# Testing & Observability Annotations

Spring's test support, test slices, Testcontainers integration, architecture tests — and metrics, tracing and Actuator endpoints. Deep dive: Chapters 15, 27, 28, 41.

## Test contexts

### `@SpringBootTest` ✅
Starts a full application context. `webEnvironment = RANDOM_PORT` starts a real server.

```java title="CheckoutFlowIT.java"
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Import(ContainersConfig.class)
class CheckoutFlowIT {

    @LocalServerPort int port;                       // org.springframework.boot.test.web.server

    @Test
    void placesAnOrder() { ... }
}
```
Keep configuration identical across test classes so the context cache is reused (Chapter 15).

### Test slices ✅
Load one layer only; collaborators are replaced with mocks.

| Slice | Loads | Example target |
|---|---|---|
| `@WebMvcTest(CartController.class)` | Controllers, advice, converters, security filters | Request/response mapping, status codes, validation |
| `@WebFluxTest` | Reactive controllers | SSE tracking endpoint |
| `@DataJpaTest` | JPA, repositories, Flyway | Queries, mappings, locking |
| `@JdbcTest` / `@DataJdbcTest` | JDBC infrastructure | `JdbcClient` repositories |
| `@DataMongoTest` / `@DataRedisTest` | Store-specific infrastructure | Document mapping, Redis ops |
| `@JsonTest` | Jackson setup | Golden-file JSON contracts |
| `@RestClientTest` | `RestClient`/`RestTemplate` + `MockRestServiceServer` | HTTP client error mapping |
| `@GraphQlTest` | GraphQL controllers | Batch mappings |

```java title="CartControllerTest.java"
@WebMvcTest(CartController.class)
class CartControllerTest {

    @Autowired MockMvcTester mvc;                    // AssertJ-style MockMvc (Boot 3.4+)
    @MockitoBean CartDelegate delegate;

    @Test
    void rejectsQuantityAboveLimit() {
        assertThat(mvc.post().uri("/api/v1/carts/{id}/items", CART_ID)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"sku\":\"ATTA-5KG\",\"quantity\":50}"))
            .hasStatus(HttpStatus.BAD_REQUEST);
    }
}
```
Boot 4 moves slice annotations into technology-specific test modules — **verify** imports (Chapter 42).

### `@AutoConfigureMockMvc` · `@AutoConfigureWebTestClient` · `@AutoConfigureTestDatabase` ✅
Add MockMvc or WebTestClient to a full `@SpringBootTest`; control embedded-database replacement.

```java title="Keep the real database (snippet)"
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)   // use Testcontainers PostgreSQL
@Import(ContainersConfig.class)
class OrderRepositoryTest { ... }
```

## Replacing beans

### `@MockitoBean` · `@MockitoSpyBean` ✅ (Framework 6.2+)
Replace or spy on a bean in the test context. Replace Boot's `@MockBean`/`@SpyBean`, removed in Boot 4.

```java title="Mocking a gateway (snippet)"
@MockitoBean PaymentGateway gateway;
@MockitoSpyBean OutboxWriter outbox;
```

### `@TestConfiguration` · `@TestBean` ✅
Test-only configuration and bean overrides via a factory method.

```java title="ContainersConfig.java"
@TestConfiguration(proxyBeanMethods = false)
public class ContainersConfig {

    @Bean
    @ServiceConnection
    PostgreSQLContainer<?> postgres() { return new PostgreSQLContainer<>("postgres:17-alpine"); }

    @Bean
    @ServiceConnection
    KafkaContainer kafka() { return new KafkaContainer("apache/kafka:3.9.0"); }
}
```

## Test infrastructure

### `@ServiceConnection` ✅
Derives connection details (URL, credentials) from a Testcontainers container bean — no `@DynamicPropertySource` needed for supported services.

### `@DynamicPropertySource` ✅
Supplies properties at runtime, for services without a `ServiceConnection` (e.g. WireMock base URLs).

```java title="WireMock base URL (snippet)"
@DynamicPropertySource
static void pricingUrl(DynamicPropertyRegistry registry) {
    registry.add("grocery.clients.pricing.base-url", wireMock::baseUrl);
}
```

### `@Testcontainers` · `@Container` ✅ (Testcontainers JUnit extension)
Manage container lifecycle in a test class. Declaring containers as beans (above) shares them across tests more effectively.

### `@DirtiesContext` ⚠️
Discards the cached context after a test. Expensive — use only when a test genuinely corrupts shared state.

### `@ActiveProfiles` · `@TestPropertySource` ✅
Activate profiles or add properties for a test. Each distinct combination creates a new cached context.

### `@Sql` · `@SqlGroup` ✅
Run SQL scripts before/after tests. Prefer builders creating data through repositories for readability.

### `@Transactional` in tests ⚠️
Rolls back after each test — convenient, but hides commit-time behaviour (after-commit listeners, outbox relays). Avoid it for integration tests of transactional flows.

### `@SpringBatchTest` ✅
`JobLauncherTestUtils` and `JobRepositoryTestUtils` for batch job tests (Chapter 33).

### `@ApplicationModuleTest` ✅ (Spring Modulith)
Bootstraps one module (and optionally its dependencies) for module-level integration tests (Chapter 37).

## JUnit Jupiter essentials

| Annotation | Use |
|---|---|
| `@Test` | A test method (`org.junit.jupiter.api.Test`) |
| `@BeforeEach` / `@AfterEach` / `@BeforeAll` / `@AfterAll` | Setup and teardown |
| `@ParameterizedTest` + `@ValueSource` / `@CsvSource` / `@MethodSource` | Data-driven tests — the access matrix (Chapter 39) |
| `@Nested` | Group related tests |
| `@Tag("ai-eval")` | Run groups separately (nightly suites) |
| `@Disabled` | Skip (with a reason and a ticket) |
| `@ExtendWith(MockitoExtension.class)` | Mockito without Spring; enables `@Mock`, `@InjectMocks` |
| `@TestFactory` | Dynamic tests — the reflective tenant leak suite (Chapter 38) |
| `@Timeout` | Fail slow tests |

```java title="Access matrix (snippet)"
@ParameterizedTest
@CsvSource({
    "CUSTOMER, /api/v1/admin/orders, 403",
    "OPS,      /api/v1/admin/orders, 200"
})
void enforcesAccess(String role, String path, int status) { ... }
```

## Architecture tests

### `@AnalyzeClasses` · `@ArchTest` ✅ (ArchUnit)

```java title="ArchitectureTest.java"
@AnalyzeClasses(packages = "in.grocery.order")
class ArchitectureTest {

    @ArchTest
    static final ArchRule domainIsFrameworkFree = noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage("org.springframework..", "jakarta.persistence..");
}
```

## Observability

### `@Observed` ✅ (Micrometer) **(proxy)**
Produces a timer metric **and** a span from one annotation. Requires the observation aspect (`management.observations.annotations.enabled=true`).

```java title="Observed checkout step (snippet)"
@Observed(name = "grocery.checkout.pricing", contextualName = "price-cart",
          lowCardinalityKeyValues = {"channel", "app"})
public PricedCart price(Cart cart) { ... }
```

### `@Timed` · `@Counted` ✅ **(proxy)**
Timer or counter for a method. Low-cardinality tags only.

```java title="Timed method (snippet)"
@Timed(value = "grocery.search.query", histogram = true)
public SearchResult search(SearchQuery query) { ... }
```

### `@NewSpan` · `@ContinueSpan` · `@SpanTag` ✅ (Micrometer Tracing)
Create or continue a span, tagging it with method arguments. Replace Sleuth's annotations of the same name.

## Actuator endpoints

### `@Endpoint` · `@ReadOperation` · `@WriteOperation` · `@DeleteOperation` · `@Selector` ✅
Custom Actuator endpoints, exposed at `/actuator/{id}` when included in `management.endpoints.web.exposure.include`.

```java title="PlatformInfoEndpoint.java"
@Component
@Endpoint(id = "platform")
class PlatformInfoEndpoint {

    @ReadOperation
    PlatformInfo info() { return new PlatformInfo(platformVersion(), SpringBootVersion.getVersion()); }

    @ReadOperation
    ErrorCodeDetail errorCode(@Selector String code) { return catalog.describe(code); }   // /actuator/platform/{code}
}
```
Secure it and keep it on the management port (Chapters 27, 41).

### `@WebEndpoint` · `@EndpointWebExtension` ✅ (rare)
HTTP-only endpoints, or web-specific extensions of an existing endpoint.

---

[:material-arrow-left: Async, Messaging & Resilience](async-messaging.md) · [Outdated → Replacement :material-arrow-right:](deprecated.md)
