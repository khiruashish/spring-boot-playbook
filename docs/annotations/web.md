# Web Layer Annotations

Spring MVC and WebFlux annotations for mapping requests, binding input, shaping responses and handling errors — plus declarative HTTP clients. Examples use the grocery **cart**, **catalog** and **order** services. Deep dive: Chapters 08, 10, 19, 20.

**Legend:** ✅ current · ⚠️ still works but prefer an alternative · ❌ removed/deprecated — see [Outdated → Replacement](deprecated.md).

---

## `@PathVariable` vs `@RequestParam` — the one everyone asks about

Both bind **parts of the URL** to method parameters. The difference is *which part* and *what it means*.

```text
GET /api/v1/stores/560102/products/ATTA-5KG?includeOutOfStock=true&page=0&size=20
                   └─ path variable ─┘      └────────────── request parameters ──────────────┘
                   (identifies the resource)  (filters, options, paging — after the "?")
```

| | `@PathVariable` | `@RequestParam` |
|---|---|---|
| Reads from | A `{placeholder}` segment in the **path** | The **query string** (`?a=1&b=2`) — and form fields in `application/x-www-form-urlencoded` bodies |
| Meaning | **Which** resource: `/orders/{ref}` | **How** to fetch or filter it: `?status=PAID&page=2` |
| Required by default | Yes — the URL doesn't match without it | Yes — `400` if missing, unless `required = false` or `defaultValue` |
| Optional values | Rare; use separate mappings instead | Common: `required = false`, `defaultValue`, `Optional<T>` |
| Multiple values | One per placeholder | Repeats allowed: `?tag=organic&tag=vegan` → `List<String>` |
| Typical REST use | IDs, slugs, hierarchy: `/sellers/{sellerId}/products/{sku}` | Search, sort, pagination, flags |
| Caching and bookmarking | Part of the resource identity | Part of the request variant |
| Encoding | Path-segment rules (`/` not allowed unencoded) | Query rules (`+`, `&`, `=` must be encoded) |

**Rule of thumb:** if removing the value gives you a *different resource* (or none), it's a path variable. If it gives you the *same resource filtered or paged differently*, it's a request parameter.

### Example: both together

```java title="ProductController.java"
package in.grocery.catalog.web;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import java.util.List;
import java.util.Optional;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/stores/{pincode}/products")               // (1)!
@Validated                                                          // (2)!
class ProductController {

    private final ProductDelegate delegate;

    ProductController(ProductDelegate delegate) {
        this.delegate = delegate;
    }

    @GetMapping("/{sku}")
    ProductView bySku(@PathVariable @Pincode String pincode,         // (3)!
                      @PathVariable String sku) {
        return delegate.find(pincode, sku);
    }

    @GetMapping
    PageView<ProductView> search(
            @PathVariable @Pincode String pincode,
            @RequestParam(required = false) String q,                                   // (4)!
            @RequestParam(defaultValue = "false") boolean includeOutOfStock,            // (5)!
            @RequestParam(name = "tag", required = false) List<String> tags,            // (6)!
            @RequestParam Optional<String> brand,                                       // (7)!
            @RequestParam(defaultValue = "0") @Min(0) int page,
            @RequestParam(defaultValue = "20") @Min(1) @Max(100) int size) {            // (8)!
        return delegate.search(pincode, q, includeOutOfStock, tags, brand, page, size);
    }
}
```

1. A placeholder at class level applies to every method in the controller.
2. Needed for constraint annotations on individual parameters (Chapter 09).
3. Names match the placeholders, so no `name` attribute is needed — as long as the code is compiled with `-parameters` (Boot's build plugins do this by default). If not, write `@PathVariable("sku")`.
4. `null` when absent.
5. `defaultValue` implies `required = false` and handles type conversion from the string `"false"`.
6. `?tag=organic&tag=vegan` → `["organic", "vegan"]`. `name` maps a singular query name to a plural Java name.
7. `Optional<T>` is another way to say "not required".
8. Always bound page sizes — an unbounded `size` is a denial-of-service vector (Chapter 20).

| Request | Result |
|---|---|
| `GET /api/v1/stores/560102/products/ATTA-5KG` | `bySku("560102", "ATTA-5KG")` |
| `GET /api/v1/stores/560102/products?q=atta&tag=organic&tag=local` | `search(..., q="atta", tags=[organic, local], page=0, size=20)` |
| `GET /api/v1/stores/560102/products?size=500` | `400` — `size` violates `@Max(100)` |
| `GET /api/v1/stores/060102/products` | `400` — invalid pincode |
| `GET /api/v1/stores/560102/products?page=abc` | `400` — `MethodArgumentTypeMismatchException` |

### Other forms

```java title="Variations (snippet)"
@GetMapping("/orders/{ref:ORD-[A-Z0-9]+}")                    // regex-constrained placeholder
OrderView byRef(@PathVariable String ref) { ... }

@GetMapping("/orders/{ref}/lines/{lineNo}")
LineView line(@PathVariable Map<String, String> vars) { ... } // all path variables as a map

@GetMapping("/products")
List<ProductView> filter(@RequestParam Map<String, String> params) { ... }   // all query params — avoid for public APIs

@GetMapping("/files/**")                                       // multi-segment remainder
Resource file(HttpServletRequest request) { ... }
```

### Pitfalls

| Pitfall | Fix |
|---|---|
| `IllegalArgumentException: Name for argument ... not specified` | Compile with `-parameters`, or add the name explicitly |
| Using `@RequestParam` for identifiers (`/orders?ref=ORD-1`) | Use a path variable — identity belongs in the path |
| Using `@PathVariable` for filters (`/products/dairy/cheap/page/2`) | Use query parameters |
| Missing parameter gives a raw 400 | Map `MissingServletRequestParameterException` in the advice to a problem body (Chapter 10) |
| Trailing slash `/orders/ORD-1/` → 404 on Boot 3+ | Trailing-slash matching is off by default since Framework 6 (Chapter 42) |
| Sensitive data in query strings | Query strings end up in logs and browser history — never tokens or personal data |

---

## Controllers and routing

### `@RestController` ✅
`org.springframework.web.bind.annotation` — `@Controller` + `@ResponseBody`: return values are serialized, typically to JSON.

```java title="CartController.java"
@RestController
@RequestMapping("/api/v1/carts")
class CartController {
    @GetMapping("/{cartId}")
    CartView get(@PathVariable UUID cartId) { return delegate.get(cartId); }
}
```
Pitfall: return DTOs, never JPA entities (Chapter 11).

### `@Controller` ✅
A web controller whose return values are view names unless the method has `@ResponseBody`. Use for server-rendered pages (the admin portal); use `@RestController` for APIs.

```java title="AdminDashboardController.java"
@Controller
class AdminDashboardController {
    @GetMapping("/admin")
    String dashboard(Model model) { model.addAttribute("pending", orders.pendingCount()); return "admin/dashboard"; }
}
```

### `@RequestMapping` ✅
Maps a path (and optionally method, headers, params, consumes, produces) to a class or method. At class level it sets a common prefix.

```java title="OrderController.java"
@RestController
@RequestMapping(path = "/api/v1/orders", produces = MediaType.APPLICATION_JSON_VALUE)
class OrderController { ... }
```
Pitfall: `@RequestMapping` on a method without `method =` matches **every** HTTP verb — use the specific shortcuts below.

### `@GetMapping` · `@PostMapping` · `@PutMapping` · `@PatchMapping` · `@DeleteMapping` ✅
Composed shortcuts for `@RequestMapping(method = …)`.

```java title="CartItemsController.java"
@PostMapping("/{cartId}/items")
ResponseEntity<CartView> add(@PathVariable UUID cartId, @Valid @RequestBody AddItemRequest req) { ... }

@PatchMapping("/{cartId}/items/{sku}")
CartView changeQuantity(@PathVariable UUID cartId, @PathVariable String sku,
                        @Valid @RequestBody ChangeQuantityRequest req) { ... }

@DeleteMapping("/{cartId}/items/{sku}")
@ResponseStatus(HttpStatus.NO_CONTENT)
void remove(@PathVariable UUID cartId, @PathVariable String sku) { ... }
```

### `version` attribute on mappings (Framework 7 / Boot 4) ✅ new
Built-in API versioning; the version comes from a header, path segment, query parameter or media type configured with `ApiVersionConfigurer`.

```java title="CartController.java (Boot 4)"
@GetMapping(path = "/{cartId}", version = "1")
CartViewV1 getV1(@PathVariable UUID cartId) { ... }

@GetMapping(path = "/{cartId}", version = "2+")      // 2 and later
CartViewV2 getV2(@PathVariable UUID cartId) { ... }
```
**Verify** syntax against your Framework version (Chapter 20).

---

## Binding request data

### `@RequestBody` ✅
Deserializes the body (JSON) into an object using the configured message converters.

```java title="AddItemRequest.java"
public record AddItemRequest(@NotBlank String sku, @Min(1) @Max(20) int quantity) {}

@PostMapping("/{cartId}/items")
CartView add(@PathVariable UUID cartId, @Valid @RequestBody AddItemRequest request) { ... }
```
Pitfalls: add `@Valid` or nothing is validated; for webhook signature checks, bind `@RequestBody byte[]` to keep the raw bytes (Chapter 18).

### `@RequestHeader` ✅
Binds a request header.

```java title="OrderController.java"
@PostMapping
ResponseEntity<OrderView> place(@RequestHeader("Idempotency-Key") String idempotencyKey,
                                @RequestHeader(value = HttpHeaders.IF_MATCH, required = false) String ifMatch,
                                @Valid @RequestBody PlaceOrderRequest request) { ... }
```
Pitfall: never trust identity headers such as `X-Customer-Id` from clients — derive identity from the token (Chapter 18).

### `@CookieValue` ✅
Binds a cookie.

```java title="Admin portal (snippet)"
@GetMapping("/admin/preferences")
Preferences prefs(@CookieValue(name = "admin_theme", defaultValue = "light") String theme) { ... }
```

### `@ModelAttribute` ✅
Binds query or form parameters onto an object (and, in MVC views, adds it to the model). Handy for many filter parameters.

```java title="ProductSearchController.java"
public record ProductFilter(String q, String brand, BigDecimal maxPrice, Integer page, Integer size) {}

@GetMapping("/api/v1/products")
PageView<ProductView> search(@Valid @ModelAttribute ProductFilter filter) { ... }   // ?q=atta&brand=Aashirvaad&maxPrice=400
```

### `@RequestPart` ✅
Binds one part of a `multipart/form-data` request — a file, or a JSON part alongside it.

```java title="SellerFeedController.java"
@PostMapping(path = "/api/v1/sellers/{sellerId}/feeds", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
FeedReceipt upload(@PathVariable String sellerId,
                   @RequestPart("file") MultipartFile file,
                   @RequestPart("meta") @Valid FeedMetadata meta) { ... }
```
Pitfall: bound upload sizes with `spring.servlet.multipart.*`, and detect content types rather than trusting them (Chapter 39).

### `@MatrixVariable` ✅ (rare)
Binds `;name=value` pairs in path segments. Disabled by default; rarely worth enabling for public APIs.

```java title="Matrix variables (snippet)"
// GET /products/atta;brand=Aashirvaad;pack=5kg
@GetMapping("/products/{name}")
ProductView find(@PathVariable String name, @MatrixVariable String brand) { ... }
```

### `@SessionAttribute` / `@RequestAttribute` ✅
Bind an existing session attribute or request attribute (set by a filter or interceptor).

```java title="Request attribute from a filter (snippet)"
@GetMapping("/api/v1/me/context")
TenantView context(@RequestAttribute("tenantId") String tenantId) { ... }
```

### `@AuthenticationPrincipal` ✅ (Spring Security)
Injects the current principal — a `Jwt`, `UserDetails` or custom type.

```java title="MeController.java"
@GetMapping("/api/v1/me")
CustomerView me(@AuthenticationPrincipal Jwt jwt) { return customers.find(jwt.getSubject()); }
```

---

## Shaping responses

### `@ResponseBody` ✅
Serialize the return value instead of resolving a view. Implied by `@RestController`.

### `@ResponseStatus` ✅
Fixed status for a handler method, or the status to use when an exception type is thrown.

```java title="Status on a handler (snippet)"
@DeleteMapping("/{cartId}")
@ResponseStatus(HttpStatus.NO_CONTENT)
void clear(@PathVariable UUID cartId) { delegate.clear(cartId); }
```
⚠️ On exception classes it works, but it produces a minimal body — prefer `ProblemDetail` via `@RestControllerAdvice` (Chapter 10). Use `ResponseEntity` when you need `Location` or `ETag` headers.

### `@CrossOrigin` ⚠️
Per-controller CORS. Works, but with Spring Security present configure CORS centrally with `http.cors(...)` so preflight requests are handled before authentication (Chapter 17).

```java title="Per-controller CORS (snippet)"
@CrossOrigin(origins = "https://admin.grocery.in", maxAge = 3600)
@RestController
class AdminReportController { ... }
```

---

## Error handling

### `@RestControllerAdvice` / `@ControllerAdvice` ✅
Global exception handling, binding and model setup across controllers. `@RestControllerAdvice` adds `@ResponseBody`.

```java title="GlobalErrorHandler.java"
@RestControllerAdvice
class GlobalErrorHandler {

    @ExceptionHandler(ProductNotFoundException.class)
    ProblemDetail notFound(ProductNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND,
                "Product %s not found".formatted(ex.sku()));
        problem.setType(URI.create("https://errors.grocery.in/product-not-found"));
        problem.setProperty("code", "PRODUCT_NOT_FOUND");
        return problem;
    }
}
```
Pitfall: exceptions thrown in filters never reach it (Chapter 10).

### `@ExceptionHandler` ✅
Handles specific exception types — in a controller (local) or an advice (global).

```java title="Local handler (snippet)"
@ExceptionHandler(StaleCartVersionException.class)
ResponseEntity<ProblemDetail> stale(StaleCartVersionException ex) {
    return ResponseEntity.status(HttpStatus.PRECONDITION_FAILED).body(problem("CART_VERSION_STALE", ex));
}
```

### `@InitBinder` ✅
Customizes data binding: allowed fields, custom editors, validators.

```java title="Restricting bindable fields (snippet)"
@InitBinder("productFilter")
void initBinder(WebDataBinder binder) {
    binder.setAllowedFields("q", "brand", "maxPrice", "page", "size");   // blocks mass assignment
}
```

---

## Declarative HTTP clients

### `@HttpExchange` and `@GetExchange` · `@PostExchange` · `@PutExchange` · `@PatchExchange` · `@DeleteExchange` ✅
Define an HTTP client as a Java interface; a proxy is backed by `RestClient` or `WebClient` (Chapter 19). Parameters use the same `@PathVariable`, `@RequestParam`, `@RequestHeader` and `@RequestBody` annotations as controllers.

```java title="PricingApi.java"
@HttpExchange("/api/v1/prices")
public interface PricingApi {

    @GetExchange("/{sku}")
    PriceResponse price(@PathVariable String sku, @RequestParam String pincode);

    @PostExchange("/bulk")
    List<PriceResponse> prices(@RequestBody BulkPriceRequest request);
}
```
Replaces `@FeignClient` for new code.

### `@ImportHttpServices` (Boot 4) ✅ new
Registers HTTP interface proxies as beans in named groups, configured with `spring.http.client.service.group.<name>.*`.

```java title="PricingClientConfig.java (Boot 4)"
@Configuration(proxyBeanMethods = false)
@ImportHttpServices(group = "pricing", types = PricingApi.class)
class PricingClientConfig {}
```
**Verify** names for your version (Chapter 19).

---

## WebFlux notes

WebFlux uses the same mapping and binding annotations (`@RestController`, `@GetMapping`, `@PathVariable`, `@RequestParam`, `@RequestBody`…) with reactive return types (`Mono<T>`, `Flux<T>`). The functional alternative (`RouterFunction`) uses no annotations at all (Chapter 31).

```java title="TrackingController.java"
@GetMapping(path = "/api/v1/deliveries/{orderRef}/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
Flux<DeliveryView> stream(@PathVariable String orderRef) { return tracking.positions(orderRef); }
```

---

[:material-arrow-left: Core Container](core-container.md) · [Validation & JSON :material-arrow-right:](validation-json.md)
