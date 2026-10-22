# Data & Transaction Annotations

JPA mapping, Spring Data repositories, auditing, locking and transactions. Deep dive: Chapters 12, 13, 16, 22, 38.

## Entity mapping (`jakarta.persistence`)

### `@Entity` · `@Table` ✅
Map a class to a table.

```java title="OrderEntity.java"
@Entity
@Table(name = "customer_order",
       indexes = @Index(name = "idx_order_customer_placed", columnList = "customer_id, placed_at DESC"))
public class OrderEntity { ... }
```
Indexes declared here are documentation only when schema comes from Flyway (Chapter 14).

### `@Id` · `@GeneratedValue` · `@SequenceGenerator` ✅
Primary key and generation strategy.

```java title="Sequence ids (snippet)"
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "order_seq")
@SequenceGenerator(name = "order_seq", sequenceName = "order_seq", allocationSize = 50)
private Long id;
```
Pitfall: `IDENTITY` disables JDBC insert batching — prefer sequences (Chapter 13).

### `@UuidGenerator` (Hibernate) ✅
UUID ids, including time-ordered variants.

```java title="UUID id (snippet)"
@Id @UuidGenerator(style = UuidGenerator.Style.TIME)
private UUID id;
```

### `@Column` · `@Enumerated` · `@Lob` · `@Transient` ✅
Column mapping details; enum storage (use `EnumType.STRING`, never `ORDINAL`); large objects; non-persistent fields.

```java title="Columns (snippet)"
@Column(name = "order_ref", nullable = false, unique = true, length = 20, updatable = false)
private String orderRef;

@Enumerated(EnumType.STRING)
@Column(nullable = false, length = 20)
private OrderStatus status;
```

### `@Version` ✅
Optimistic locking — the update fails if another transaction changed the row. Also a natural ETag source (Chapter 08).

```java title="Optimistic locking (snippet)"
@Version
private long version;
```

### `@Embeddable` · `@Embedded` · `@AttributeOverride` ✅
Value objects stored in the owning table.

```java title="Embedded value object (snippet)"
@Embeddable
public record DeliveryAddressEmbeddable(String line1, String city, String pincode) {}

@Embedded
@AttributeOverride(name = "pincode", column = @Column(name = "delivery_pincode"))
private DeliveryAddressEmbeddable deliveryAddress;
```

### `@ManyToOne` · `@OneToMany` · `@OneToOne` · `@ManyToMany` · `@JoinColumn` ✅
Relationships.

```java title="Order and lines (snippet)"
@OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
private List<OrderLineEntity> lines = new ArrayList<>();

// in OrderLineEntity
@ManyToOne(fetch = FetchType.LAZY, optional = false)          // set LAZY — the default is EAGER
@JoinColumn(name = "order_id")
private OrderEntity order;
```
Pitfalls: eager `@ManyToOne` defaults; `@ManyToMany` rarely survives real requirements (model the join table as an entity); cross-aggregate references should be ids (Chapter 37).

### `@Convert` · `@Converter` ✅
Custom attribute conversion — value objects, encrypted fields (Chapter 39).

```java title="Encrypted column (snippet)"
@Convert(converter = EncryptedStringConverter.class)
@Column(name = "bank_account_number")
private String bankAccountNumber;
```

### `@JdbcTypeCode` (Hibernate) ✅
Maps a Java type to a JDBC type, e.g. JSON columns — replaces Hibernate 5's `@Type(type = "jsonb")`.

```java title="JSON attributes (snippet)"
@JdbcTypeCode(SqlTypes.JSON)
private Map<String, Object> attributes;
```

### `@SQLRestriction` (Hibernate) ✅
Adds a SQL predicate to every load — soft deletes. Replaces `@Where`.

```java title="Soft delete (snippet)"
@Entity
@SQLRestriction("deleted = false")
public class ProductEntity { ... }
```

### `@TenantId` (Hibernate 6+) ✅
Discriminator multi-tenancy: adds the tenant predicate to queries and sets it on insert (Chapter 38). Doesn't cover native SQL — pair with row-level security.

```java title="Tenant column (snippet)"
@TenantId
@Column(name = "tenant_id", nullable = false, updatable = false)
private String tenantId;
```

### `@PrePersist` · `@PreUpdate` · `@PostLoad` · `@EntityListeners` ✅
Entity lifecycle callbacks. Keep them trivial — they run inside flushes.

## Spring Data repositories

### `@Query` ✅
Custom JPQL or native SQL on a repository method.

```java title="OrderRepository.java"
public interface OrderRepository extends JpaRepository<OrderEntity, Long> {

    @Query("""
           select o from OrderEntity o
           where o.customerId = :customerId and o.placedAt < :before
           order by o.placedAt desc
           """)
    List<OrderEntity> recentForCustomer(String customerId, Instant before, Limit limit);

    @Query(value = "select * from customer_order where status = 'PLACED' for update skip locked limit :n",
           nativeQuery = true)
    List<OrderEntity> claimPlaced(int n);
}
```
Native queries bypass Hibernate filters such as `@TenantId`.

### `@Modifying` ✅
Marks an update/delete query.

```java title="Bulk update (snippet)"
@Modifying(clearAutomatically = true)
@Query("update CartEntity c set c.status = 'ABANDONED' where c.updatedAt < :cutoff and c.status = 'ACTIVE'")
int abandonOlderThan(Instant cutoff);
```
Pitfall: bypasses the persistence context — clear it, or loaded entities are stale.

### `@EntityGraph` ✅
Fetch plan per query — the standard N+1 fix.

```java title="Fetch lines with orders (snippet)"
@EntityGraph(attributePaths = {"lines"})
Optional<OrderEntity> findByOrderRef(String orderRef);
```

### `@Lock` ✅
Pessimistic or optimistic locking on a repository method.

```java title="Pessimistic lock (snippet)"
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("select s from StockEntity s where s.sku = :sku and s.hubId = :hubId")
Optional<StockEntity> lockStock(String sku, String hubId);
```

### `@Param` ✅
Names a query parameter — only needed when the code isn't compiled with `-parameters`.

### `@QueryHints` · `@NativeQuery` · `@Procedure` ✅ (occasional)
JPA hints (fetch size, read-only), a shorthand for native queries, stored procedure calls.

### `@EnableJpaRepositories` · `@EnableMongoRepositories` · `@EnableRedisRepositories` ✅
Only needed for non-standard repository locations — Boot enables repositories automatically.

## Auditing

### `@EnableJpaAuditing` · `@CreatedDate` · `@LastModifiedDate` · `@CreatedBy` · `@LastModifiedBy` ✅
Automatic timestamps and actors on entities.

```java title="Auditable entity (snippet)"
@EntityListeners(AuditingEntityListener.class)
@MappedSuperclass
public abstract class Audited {
    @CreatedDate private Instant createdAt;
    @LastModifiedDate private Instant updatedAt;
    @CreatedBy private String createdBy;
}

@Configuration(proxyBeanMethods = false)
@EnableJpaAuditing(auditorAwareRef = "currentActor", dateTimeProviderRef = "auditClock")
class AuditingConfig {}
```
For security-grade audit trails use a separate append-only log (Chapter 39).

### `@MappedSuperclass` ✅
Shares mapped fields across entities without a table of its own.

## Transactions

### `@Transactional` ✅ (Spring) **(proxy)**
Declarative transaction boundary.

```java title="OrderService.java"
@Service
public class OrderService {

    @Transactional
    public Order place(PlaceOrderCommand command, List<PricedLine> pricedLines) {   // prices fetched BEFORE
        Order order = Order.place(command, pricedLines);
        orders.save(order);
        outbox.append("order", order.ref(), "OrderPlaced", OrderPlacedEvent.from(order));
        return order;
    }

    @Transactional(readOnly = true)
    public OrderView find(String orderRef, String customerId) { ... }
}
```

| Attribute | Use |
|---|---|
| `readOnly = true` | Skips dirty checking; hints for replicas |
| `propagation = REQUIRES_NEW` | Independent transaction (audit records) — holds a second connection |
| `propagation = MANDATORY` | Must join an existing one — outbox writes |
| `rollbackFor = SomeCheckedException.class` | Checked exceptions don't roll back by default |
| `timeout = 5` | Bound long transactions (seconds) |
| `isolation = …` | Rarely changed; PostgreSQL default is read committed |

Pitfalls: private methods and self-invocation get no transaction; remote calls inside a transaction hold connections; use Spring's annotation, not `jakarta.transaction.Transactional` (Chapter 16).

### `@EnableTransactionManagement` ✅
Enables annotation-driven transactions — Boot does this automatically.

## NoSQL mapping (selected)

### `@Document` · `@Indexed` · `@Field` (Spring Data MongoDB) ✅

```java title="ProductReviewDocument.java"
@Document("product_reviews")
@CompoundIndex(def = "{'sku': 1, 'createdAt': -1}")
public record ProductReviewDocument(@Id String id, String sku, @Field("rating") int stars, String text, Instant createdAt) {}
```

### `@RedisHash` · `@TimeToLive` (Spring Data Redis) ✅
Repository-style Redis entities — for most caching, use `@Cacheable` or templates instead (Chapters 21, 22).

---

[:material-arrow-left: Validation & JSON](validation-json.md) · [Security :material-arrow-right:](security.md)
