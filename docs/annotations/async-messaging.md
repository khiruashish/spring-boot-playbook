# Async, Scheduling, Caching, Messaging & Resilience Annotations

Everything that runs later, runs elsewhere, runs repeatedly or protects a call. Deep dive: Chapters 21, 23, 24, 25, 26, 32, 33, 37, 40.

## Async and scheduling **(proxy)**

### `@EnableAsync` · `@Async` ✅
Run a method on an executor. Name the executor — the default queue is effectively unbounded.

```java title="AsyncConfig.java"
@Configuration(proxyBeanMethods = false)
@EnableAsync
class AsyncConfig {
    @Bean
    ThreadPoolTaskExecutor notificationExecutor() {
        var executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(16);
        executor.setQueueCapacity(200);                                  // bounded
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setTaskDecorator(new ContextPropagatingTaskDecorator()); // MDC + tracing
        return executor;
    }
}
```
```java title="Sending asynchronously (snippet)"
@Async("notificationExecutor")
public CompletableFuture<Void> sendOrderSms(String mobile, String orderRef) { ... }
```
Pitfalls: self-invocation runs synchronously; transactions and (by default) security context don't propagate; `void` methods need an `AsyncUncaughtExceptionHandler` (Chapter 25).

### `@EnableScheduling` · `@Scheduled` ✅
Periodic work. Set `zone`, size the scheduler pool (default 1), and lock across pods.

```java title="CartExpiryJob.java"
@Scheduled(cron = "0 */5 * * * *", zone = "Asia/Kolkata")
@SchedulerLock(name = "expire-carts", lockAtMostFor = "PT4M")
public void expireStaleCarts() { carts.expireOlderThan(Duration.ofHours(24)); }
```
`fixedDelay` waits after the previous run (no overlap); `fixedRate` starts on a fixed cadence.

### `@SchedulerLock` (ShedLock) · `@EnableSchedulerLock` ✅
Ensures one pod runs a scheduled job at a time. It's mutual exclusion, not idempotency — jobs must still be safe to re-run.

## Caching **(proxy)**

### `@EnableCaching` · `@Cacheable` ✅
Return the cached value, or compute and store it.

```java title="PricingService.java"
@Cacheable(cacheNames = "price", key = "#sku + '|' + #pincode", sync = true)
public PriceView priceFor(String sku, String pincode) { return prices.lookup(sku, pincode); }
```
Pitfalls: keys must include every dimension (pincode, tenant, customer); `sync` prevents stampedes per JVM only (Chapter 21).

### `@CachePut` · `@CacheEvict` · `@Caching` · `@CacheConfig` ✅
Update, evict, combine cache operations, and set class-level defaults.

```java title="Evict after a price change (snippet)"
@CacheConfig(cacheNames = "price")
public class PriceAdminService {

    @CacheEvict(key = "#sku + '|' + #pincode")
    public void changePrice(String sku, String pincode, Money newPrice) { ... }

    @CacheEvict(allEntries = true)
    public void reloadPromotions() { ... }
}
```
Evict **after commit** when the change is transactional — see Chapter 21's event-based pattern.

## Kafka (Spring for Apache Kafka)

### `@KafkaListener` ✅
Consumes records; concurrency ≤ partition count; handlers must be idempotent.

```java title="OrderPlacedConsumer.java"
@KafkaListener(topics = "grocery.order.placed.v1", groupId = "inventory-service", concurrency = "3")
public void onOrderPlaced(OrderPlacedEvent event,
                          @Header(KafkaHeaders.RECEIVED_KEY) String orderRef,
                          @Header("X-Tenant-Id") String tenantId) {
    TenantContext.runAs(tenantId, () -> reservations.reserve(event));
}
```

### `@RetryableTopic` · `@DltHandler` ✅
Non-blocking retries via retry topics, then a dead-letter handler. Loses per-key ordering.

```java title="Retry topics (snippet)"
@RetryableTopic(attempts = "4", backoff = @Backoff(delay = 1000, multiplier = 2.0),
                exclude = {InvalidEventException.class})
@KafkaListener(topics = "grocery.notification.requested.v1", groupId = "notification-service")
public void send(NotificationRequested event) { ... }

@DltHandler
public void deadLetter(NotificationRequested event, @Header(KafkaHeaders.EXCEPTION_MESSAGE) String error) {
    alerts.deadLetter("notification", event.id(), error);
}
```

### `@Header` · `@Payload` · `@Headers` ✅
Bind message headers and payload in any messaging listener.

### `@EnableKafka` ✅
Enables listener processing — automatic in Boot.

## RabbitMQ, JMS, Pulsar

### `@RabbitListener` · `@RabbitHandler` · `@EnableRabbit` ✅

```java title="DispatchTaskConsumer.java"
@RabbitListener(queues = "dispatch.tasks.express", concurrency = "4-8")
public void assign(DispatchTask task) { dispatcher.assignRider(task); }
```
Set `default-requeue-rejected: false` and a dead-letter exchange — otherwise poison messages loop (Chapter 24).

### `@JmsListener` · `@EnableJms` ✅
JMS consumers for enterprise brokers (e.g. an ERP integration).

```java title="ErpInvoiceListener.java"
@JmsListener(destination = "erp.invoices", concurrency = "2-4")
public void onInvoice(ErpInvoice invoice) { invoices.importFromErp(invoice); }
```

### `@PulsarListener` ✅
Pulsar consumers; choose the subscription type (`Key_Shared` for per-key ordering).

## WebSocket / STOMP, GraphQL, gRPC

### `@MessageMapping` · `@SendTo` · `@SendToUser` · `@SubscribeMapping` ✅

```java title="RiderController.java"
@MessageMapping("/rider.location")
public void location(RiderLocation location, Principal rider) { tracking.update(rider.getName(), location); }
```
Use a broker relay when running several pods (Chapter 32).

### `@QueryMapping` · `@MutationMapping` · `@SubscriptionMapping` · `@SchemaMapping` · `@BatchMapping` · `@Argument` ✅ (Spring for GraphQL)

```java title="OrderGraphController.java"
@Controller
class OrderGraphController {

    @QueryMapping
    List<OrderView> orders(@Argument int last, @AuthenticationPrincipal Jwt jwt) {
        return orders.recentForCustomer(jwt.getSubject(), last);
    }

    @BatchMapping(typeName = "OrderLine", field = "product")                 // N+1-safe
    Map<OrderLineView, ProductView> product(List<OrderLineView> lines) {
        return catalog.productsFor(lines);
    }
}
```

### `@GrpcService` ✅ (starter-dependent — verify import)
Registers a gRPC service implementation.

## Resilience **(proxy)**

### Resilience4j: `@CircuitBreaker` · `@Retry` · `@Bulkhead` · `@RateLimiter` · `@TimeLimiter` ✅

```java title="PricingGateway.java"
@CircuitBreaker(name = "pricing", fallbackMethod = "cachedPrice")
@Retry(name = "pricing")
@Bulkhead(name = "pricing")
public PriceView price(String sku, String pincode) { return pricingApi.price(sku, pincode).toView(); }

private PriceView cachedPrice(String sku, String pincode, Throwable cause) {
    return lastKnown.find(sku, pincode)
            .map(PriceView::markStale)
            .orElseThrow(() -> new DependencyUnavailableException("pricing", cause));
}
```
Configuration lives in `resilience4j.*` properties. Retry must wrap the breaker; business exceptions must not open it (Chapter 26).

### Framework 7: `@EnableResilientMethods` · `@Retryable` · `@ConcurrencyLimit` ✅ new (verify)
Core retry and concurrency limiting without extra libraries.

```java title="InventoryGateway.java (Framework 7)"
@Retryable(includes = DependencyException.class, maxRetries = 2, delay = 100, jitter = 50, multiplier = 2)
@ConcurrencyLimit(20)
public StockView stock(String sku, String hubId) { ... }
```
Don't combine it with Resilience4j retries on the same call — one retry layer only.

### Spring Retry: `@EnableRetry` · `@Retryable` · `@Recover` 🧊
Still works; in maintenance — see [Outdated → Replacement](deprecated.md) (row 35).

## Batch and Modulith

### `@StepScope` · `@JobScope` ✅ (Spring Batch)
Late-bound beans that can read job parameters.

```java title="Reader with job parameters (snippet)"
@Bean
@StepScope
JdbcPagingItemReader<OrderLine> settlementReader(DataSource dataSource,
                                                 @Value("#{jobParameters['periodStart']}") LocalDate start) { ... }
```

### `@ApplicationModuleListener` ✅ (Spring Modulith)
Transactional, asynchronous, persisted module event listener — the in-process outbox (Chapter 37).

```java title="LoyaltyModule.java"
@ApplicationModuleListener
void on(OrderPaid event) { points.award(event.customerId(), event.total()); }
```

## Spring AI

### `@Tool` · `@ToolParam` ✅ (verify for your version)
Expose methods to a model as callable tools. The identity must come from the session, never from model-supplied parameters (Chapter 40).

```java title="SupportTools.java"
@Tool(description = "Get the status of an order belonging to the current customer")
public OrderStatusView getOrderStatus(@ToolParam(description = "Order reference") String orderRef) {
    return orders.findForCustomer(orderRef, CurrentUser.require().customerId())
            .map(OrderStatusView::from)
            .orElseThrow(() -> new OrderNotFoundException(orderRef));
}
```

---

[:material-arrow-left: Security](security.md) · [Testing & Observability :material-arrow-right:](testing-observability.md)
