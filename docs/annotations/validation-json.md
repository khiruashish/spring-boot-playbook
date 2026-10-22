# Validation & JSON Annotations

Jakarta Bean Validation constraints, Spring's validation triggers, and Jackson serialization annotations. Deep dive: Chapters 09, 11.

## Triggering validation

### `@Valid` ✅ (`jakarta.validation`)
Validates the annotated argument and cascades into nested objects and collection elements.

```java title="PlaceOrderRequest.java"
public record PlaceOrderRequest(
        @NotBlank String cartId,
        @Valid @NotNull DeliveryAddress address,                 // (1)!
        @NotEmpty List<@Valid OrderLineRequest> lines) {}        // (2)!

@PostMapping
ResponseEntity<OrderView> place(@Valid @RequestBody PlaceOrderRequest request) { ... }
```

1. Without `@Valid` here, the address's own constraints are never checked.
2. Container element validation: each line is validated.

### `@Validated` ✅ (Spring)
Enables **method validation** on a bean (parameters and return values) and supports **validation groups**. **(proxy)**

```java title="Parameter validation (snippet)"
@RestController
@Validated
class DeliverySlotController {
    @GetMapping("/api/v1/slots")
    List<SlotView> slots(@RequestParam @Pincode String pincode,
                         @RequestParam @FutureOrPresent LocalDate date) { ... }
}
```
```java title="Groups (snippet)"
public interface OnCreate {}
public interface OnUpdate {}

public record ProductRequest(@Null(groups = OnCreate.class) @NotNull(groups = OnUpdate.class) Long id,
                             @NotBlank String name) {}

@PostMapping ProductView create(@Validated(OnCreate.class) @RequestBody ProductRequest r) { ... }
```

## Built-in constraints (`jakarta.validation.constraints`)

| Annotation | Checks | Grocery example |
|---|---|---|
| `@NotNull` | Not null | `@NotNull PaymentMethod method` |
| `@NotBlank` | String not null and not only whitespace | `@NotBlank String sku` |
| `@NotEmpty` | String/collection/map not null and not empty | `@NotEmpty List<OrderLineRequest> lines` |
| `@Null` | Must be null | Server-assigned id on create |
| `@Size(min, max)` | Length or size | `@Size(max = 200) String deliveryNote` |
| `@Min` / `@Max` | Integer bounds | `@Min(1) @Max(20) int quantity` |
| `@DecimalMin` / `@DecimalMax` | Decimal bounds (as strings) | `@DecimalMin("0.00") BigDecimal price` |
| `@Positive` / `@PositiveOrZero` | > 0 / ≥ 0 | `@PositiveOrZero BigDecimal deliveryFee` |
| `@Negative` / `@NegativeOrZero` | < 0 / ≤ 0 | Adjustments |
| `@Digits(integer, fraction)` | Digit counts | `@Digits(integer = 7, fraction = 2) BigDecimal amount` |
| `@Pattern(regexp)` | Regex | `@Pattern(regexp = "[A-Z0-9-]{3,40}") String sku` |
| `@Email` | Email syntax | `@Email String email` |
| `@Past` / `@PastOrPresent` | Date in the past | `@Past LocalDate dateOfBirth` |
| `@Future` / `@FutureOrPresent` | Date in the future | `@FutureOrPresent LocalDate deliveryDate` |
| `@AssertTrue` / `@AssertFalse` | Boolean value; on methods for cross-field rules | `@AssertTrue boolean isSlotWithinWindow()` |

```java title="DeliveryAddress.java"
public record DeliveryAddress(
        @NotBlank @Size(max = 120) String line1,
        @Size(max = 120) String line2,
        @NotBlank String city,
        @Pincode String pincode,
        @IndianMobile String contactMobile) {}
```

## Custom constraints

### `@Constraint` ✅
Meta-annotation that turns your annotation into a constraint, paired with a `ConstraintValidator`.

```java title="Pincode.java"
@Documented
@Constraint(validatedBy = PincodeValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.RECORD_COMPONENT, ElementType.TYPE_USE})
@Retention(RetentionPolicy.RUNTIME)
public @interface Pincode {
    String message() default "{grocery.validation.pincode}";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```
```java title="PincodeValidator.java"
public class PincodeValidator implements ConstraintValidator<Pincode, String> {
    private static final Pattern VALID = Pattern.compile("[1-9][0-9]{5}");
    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        return value == null || VALID.matcher(value).matches();     // null handled by @NotNull
    }
}
```
The handbook's platform also defines `@IndianMobile` and `@Gstin` this way (Chapter 09). Class-level constraints (annotation on the record) handle cross-field rules such as "slot end after slot start".

### `@GroupSequence` ✅ (rare)
Orders group validation — cheap checks first, expensive ones only if those pass.

## Jackson annotations (`com.fasterxml.jackson.annotation`)

### `@JsonProperty` ✅
Renames a property or marks a constructor parameter.

```java title="RazorpayOrderResponse.java"
public record RazorpayOrderResponse(String id,
                                    @JsonProperty("amount_paid") long amountPaidPaise,
                                    String status) {}
```
Pitfall: renaming a public field is a breaking API change (Chapter 20).

### `@JsonIgnore` · `@JsonIgnoreProperties` ✅
Exclude a property / ignore unknown or listed properties.

```java title="Tolerant reader (snippet)"
@JsonIgnoreProperties(ignoreUnknown = true)
public record PartnerWebhook(String event, Map<String, Object> payload) {}
```
Prefer separate DTOs over `@JsonIgnore` on entities; prefer the global `fail-on-unknown-properties: false` over per-class annotations.

### `@JsonInclude` ✅
Omit nulls or empty values.

```java title="Omit nulls (snippet)"
@JsonInclude(JsonInclude.Include.NON_NULL)
public record OrderView(String orderRef, String status, String cancellationReason) {}
```

### `@JsonFormat` ✅
Format for dates, numbers and enums.

```java title="Explicit date format (snippet)"
public record SlotView(@JsonFormat(pattern = "yyyy-MM-dd") LocalDate date, LocalTime from, LocalTime to) {}
```
Prefer global ISO-8601 configuration; use this for partner APIs with fixed formats.

### `@JsonValue` · `@JsonCreator` ✅
Serialize a value object as a single value and construct it back.

```java title="Money.java"
public record Money(BigDecimal amount) {
    @JsonCreator public static Money of(String value) { return new Money(new BigDecimal(value)); }
    @JsonValue public String json() { return amount.setScale(2, RoundingMode.HALF_UP).toPlainString(); }   // "578.00"
}
```

### `@JsonTypeInfo` · `@JsonSubTypes` ✅ (with care)
Polymorphic JSON with an explicit, allow-listed set of subtypes.

```java title="PaymentMethodDetails.java"
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes({
    @JsonSubTypes.Type(value = UpiDetails.class, name = "UPI"),
    @JsonSubTypes.Type(value = CardTokenDetails.class, name = "CARD")
})
public sealed interface PaymentMethodDetails permits UpiDetails, CardTokenDetails {}
```
Never enable default typing or `Id.CLASS` for untrusted input — a known deserialization attack vector (Chapter 11).

### `@JsonUnwrapped` · `@JsonAlias` · `@JsonPropertyOrder` · `@JsonView` ✅
Flatten a nested object; accept alternative names on input; control field order; select fields per view. Useful occasionally — separate DTOs are usually clearer than views.

```java title="Accepting a legacy field name (snippet)"
public record AddItemRequest(@JsonAlias("productCode") String sku, int quantity) {}
```

### `@JsonNaming` ✅
Naming strategy per class (e.g. snake_case for a partner API).

```java title="Partner DTO (snippet)"
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record ShiprocketShipment(String orderId, String courierName, String awbCode) {}
```

## Boot's Jackson integration

### `@JsonComponent` ⚠️ (Boot 3) → `@JacksonComponent` (Boot 4, verify)
Registers custom serializers/deserializers as beans with Boot's `ObjectMapper`.

```java title="MoneyJsonComponent.java"
@JsonComponent                         // Boot 4: @JacksonComponent (verify)
public class MoneyJsonComponent {
    public static class Serializer extends JsonSerializer<Money> { ... }
    public static class Deserializer extends JsonDeserializer<Money> { ... }
}
```

### `@JsonMixin` ⚠️ (Boot 3) → `@JacksonMixin` (Boot 4, verify)
Registers a mix-in to add annotations to a class you can't modify.

---

[:material-arrow-left: Web Layer](web.md) · [Data & Transactions :material-arrow-right:](data.md)
