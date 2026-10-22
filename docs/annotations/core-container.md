# Core Container Annotations

Bean definition, injection, scopes, lifecycle, events and conditions — the annotations that everything else in Spring builds on. Deep dive: Chapters 02, 03, 04.

**Legend:** ✅ current · ⚠️ works, prefer an alternative · ❌ removed — see [Outdated → Replacement](deprecated.md). **(proxy)** means the annotation only takes effect through a Spring proxy: public methods, no self-invocation (Chapter 04).

## Declaring beans

### `@Component` · `@Service` · `@Repository` · `@Controller` ✅
`org.springframework.stereotype` — mark a class for component scanning. The specializations communicate intent; `@Repository` also translates persistence exceptions into Spring's `DataAccessException` hierarchy.

```java title="PricingService.java"
@Service
public class PricingService {
    private final PriceRepository prices;
    public PricingService(PriceRepository prices) { this.prices = prices; }
}
```
Pitfall: a class outside the `@SpringBootApplication` package tree is never scanned.

### `@Configuration` ✅
Declares a class containing `@Bean` methods.

```java title="ClockConfig.java"
@Configuration(proxyBeanMethods = false)
class ClockConfig {
    @Bean
    Clock clock() { return Clock.system(ZoneId.of("Asia/Kolkata")); }
}
```
Use `proxyBeanMethods = false` unless one `@Bean` method calls another and must receive the singleton — faster startup, no CGLIB subclass (Chapter 02).

### `@Bean` ✅
Registers the return value of a method as a bean. Use it for third-party classes you can't annotate, or when construction needs logic.

```java title="RazorpayClientConfig.java"
@Bean
RestClient razorpayRestClient(RestClient.Builder builder, RazorpayProperties props) {
    return builder.baseUrl(props.baseUrl().toString()).build();
}
```
Pitfall: `BeanFactoryPostProcessor` and `BeanPostProcessor` bean methods should be `static` so they don't force early creation of the configuration class.

### `@Import` ✅
Pulls other configuration classes (or `ImportSelector`s/registrars) into a configuration.

```java title="PlatformConfig.java"
@Configuration(proxyBeanMethods = false)
@Import({ClockConfig.class, JsonConfig.class})
class PlatformConfig {}
```

### `@ComponentScan` ✅
Customizes scanning. Usually implicit through `@SpringBootApplication`; add it only for unusual layouts.

```java title="Scanning an extra package (snippet)"
@SpringBootApplication
@ComponentScan(basePackages = {"in.grocery.order", "in.grocery.shared.web"})
public class OrderApplication { ... }
```

### `@Description` ✅ (rare)
Adds human-readable text to a bean definition (shown in tooling).

## Injection

### `@Autowired` ⚠️ on fields · ✅ on constructors (optional)
Requests injection. With a single constructor it's unnecessary; on fields it hides dependencies and blocks immutability.

```java title="OrderService.java"
@Service
public class OrderService {
    private final OrderRepository orders;
    public OrderService(OrderRepository orders) { this.orders = orders; }   // no @Autowired needed
}
```
Use `@Autowired` only to select one of several constructors.

### `@Qualifier` ✅
Chooses among several beans of the same type.

```java title="Choosing a gateway (snippet)"
public CheckoutService(@Qualifier("razorpay") PaymentGateway gateway) { this.gateway = gateway; }
```
A custom qualifier annotation (meta-annotated with `@Qualifier`) is type-safe and refactor-friendly:

```java title="Razorpay.java"
@Qualifier
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.PARAMETER, ElementType.METHOD})
public @interface Razorpay {}
```

### `@Primary` ✅
Default candidate when several beans match and no qualifier is given.

```java title="Default gateway (snippet)"
@Bean @Primary
PaymentGateway defaultGateway(RazorpayGateway razorpay) { return razorpay; }
```
Pitfall: `@Primary` hides ambiguity; for important choices, qualify explicitly.

### `@Value` ⚠️ for groups of settings · ✅ for one-offs
Injects a property or SpEL expression.

```java title="Single value (snippet)"
public OrderSweeper(@Value("${grocery.order.auto-cancel-unpaid-after:15m}") Duration timeout) { ... }
```
For anything with more than one or two settings, use `@ConfigurationProperties` records (Chapter 06).

### `@Lookup` ✅ (rare)
Method injection — Spring overrides the method to return a fresh bean (e.g. a prototype) on each call. `ObjectProvider<T>` is usually simpler.

```java title="ObjectProvider alternative (snippet)"
public ReportService(ObjectProvider<ReportBuilder> builders) { this.builders = builders; }
ReportBuilder newBuilder() { return builders.getObject(); }
```

### `@Inject` · `@Named` (Jakarta) ✅
Standard equivalents of `@Autowired` and `@Qualifier` from `jakarta.inject` (was `javax.inject` before Boot 3). Rarely needed in Spring code.

## Scopes and creation

### `@Scope` ✅
Bean scope: `singleton` (default), `prototype`, `request`, `session`, `application`.

```java title="Prototype (snippet)"
@Component
@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
class InvoiceRenderer { ... }
```
Pitfall: a prototype injected into a singleton is injected **once** — use `ObjectProvider`.

### `@RequestScope` · `@SessionScope` · `@ApplicationScope` ✅
Shortcuts for web scopes (proxied by default).

```java title="Per-request context (snippet)"
@Component
@RequestScope
class RequestAudit { private final Instant startedAt = Instant.now(); }
```

### `@Lazy` ⚠️
Creates the bean (or the injected proxy) on first use. Moves failures from startup to runtime; useful for rarely used, expensive beans. Not a fix for circular dependencies.

### `@DependsOn` ⚠️
Forces initialization order. Usually a sign that the dependency should be injected explicitly or handled by `SmartLifecycle` (Chapter 03).

### `@Order` ✅
Ordering for collections of beans, filters, aspects, advisors and listeners. Lower values run first.

```java title="Ordered filter (snippet)"
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
class CorrelationIdFilter extends OncePerRequestFilter { ... }
```

## Lifecycle

### `@PostConstruct` · `@PreDestroy` ✅ (`jakarta.annotation`)
Run after injection / before destruction.

```java title="PincodeDirectory.java"
@Component
class PincodeDirectory {
    private Set<String> serviceable;

    @PostConstruct
    void load() { serviceable = Set.copyOf(repository.findServiceablePincodes()); }

    @PreDestroy
    void close() { log.info("Pincode directory shutting down"); }
}
```
Pitfall: runs on the raw target, not through proxies — `@Transactional` inside `@PostConstruct` doesn't apply. Use an `ApplicationRunner` for work needing proxies or readiness gating. Package changed from `javax.annotation` in Boot 3.

## Events

### `@EventListener` ✅
Handles application events, optionally filtered with a SpEL `condition`.

```java title="StockAlertListener.java"
@EventListener(condition = "#event.available() < 10")
void onLowStock(StockChanged event) { alerts.lowStock(event.sku(), event.hub()); }
```
Runs synchronously inside the publisher's transaction.

### `@TransactionalEventListener` ✅
Runs at a transaction phase — by default **after commit** — so reactions never happen for rolled-back work.

```java title="OrderNotifications.java"
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
@Async("notificationExecutor")
void orderPlaced(OrderPlaced event) { sms.send(event.mobile(), "Order " + event.orderRef() + " confirmed"); }
```
Pitfall: writing to the database from an after-commit listener needs `@Transactional(propagation = REQUIRES_NEW)` (Chapter 03).

## Conditions and profiles

### `@Profile` ✅
Registers a bean only when a profile is active.

```java title="Local stub (snippet)"
@Bean
@Profile("local")
PaymentGateway fakeGateway() { return new AlwaysApprovesGateway(); }
```
Prefer properties (`@ConditionalOnProperty`) for feature flags; keep profiles for environments.

### `@Conditional` ✅
Registers a bean when a custom `Condition` matches. Boot's `@ConditionalOn…` family is built on it ([Boot annotations](boot.md)).

## AOP

### `@Aspect` · `@Around` · `@Before` · `@After` · `@AfterReturning` · `@AfterThrowing` · `@Pointcut` ✅
Define aspects (AspectJ annotation style; Spring AOP runtime).

```java title="IdempotencyAspect.java"
@Aspect
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 100)
class IdempotencyAspect {

    @Pointcut("@annotation(in.grocery.platform.idempotency.Idempotent)")
    void idempotentOperation() {}

    @Around("idempotentOperation()")
    Object around(ProceedingJoinPoint pjp) throws Throwable {
        String key = currentIdempotencyKey();
        return store.findResult(key).orElseGet(() -> store.saveResult(key, proceed(pjp)));
    }
}
```
Pitfall: aspects only intercept calls through the proxy; order them explicitly relative to `@Transactional` (Chapter 04).

### `@EnableAspectJAutoProxy` ✅
Enables `@Aspect` processing — already on in Boot via auto-configuration.

---

[:material-arrow-left: Annotations Home](index.md) · [Spring Boot :material-arrow-right:](boot.md)
