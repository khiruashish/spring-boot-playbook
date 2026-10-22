# Security Annotations

Spring Security configuration, method-level authorization and security testing. Deep dive: Chapters 17, 18, 39.

## Configuration

### `@EnableWebSecurity` ✅
Enables Spring Security's web support. In Boot applications it's applied automatically; add it when you want to be explicit or when customizing debug output. Configuration itself is done with `SecurityFilterChain` beans — **not** by extending `WebSecurityConfigurerAdapter`, which was removed in Security 6.

```java title="SecurityConfig.java"
@Configuration(proxyBeanMethods = false)
@EnableWebSecurity
@EnableMethodSecurity
class SecurityConfig {

    @Bean
    @Order(1)
    SecurityFilterChain actuator(HttpSecurity http) throws Exception {
        return http.securityMatcher(EndpointRequest.toAnyEndpoint())
                .authorizeHttpRequests(a -> a
                        .requestMatchers(EndpointRequest.to("health", "prometheus")).permitAll()
                        .anyRequest().hasRole("OPS"))
                .build();
    }

    @Bean
    @Order(2)
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        return http.securityMatcher("/api/**")
                .authorizeHttpRequests(a -> a
                        .requestMatchers(HttpMethod.GET, "/api/v1/products/**").permitAll()
                        .anyRequest().authenticated())
                .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .csrf(AbstractHttpConfigurer::disable)
                .build();
    }
}
```

### `@EnableWebFluxSecurity` · `@EnableReactiveMethodSecurity` ✅
Reactive equivalents, configured with `SecurityWebFilterChain` beans (Chapter 31).

### `@EnableMethodSecurity` ✅
Enables `@PreAuthorize`, `@PostAuthorize`, `@PreFilter`, `@PostFilter` (on by default), and optionally `@Secured` (`securedEnabled = true`) and `@RolesAllowed` (`jsr250Enabled = true`). Replaces `@EnableGlobalMethodSecurity`.

## Method authorization **(proxy)**

### `@PreAuthorize` ✅
Checks an expression **before** the method runs.

```java title="OrderQueryService.java"
@PreAuthorize("hasRole('OPS') or @orderAccess.isOwner(#orderRef, authentication)")
public OrderView find(String orderRef) { ... }
```
```java title="OrderAccess.java"
@Component("orderAccess")
class OrderAccess {
    boolean isOwner(String orderRef, Authentication auth) {
        return orders.customerIdOf(orderRef).map(id -> id.equals(auth.getName())).orElse(false);
    }
}
```
Keep expressions short; delegate real logic to a bean so it can be unit-tested.

### `@PostAuthorize` ✅
Checks after the method returns, with access to `returnObject`.

```java title="Post-check on the result (snippet)"
@PostAuthorize("returnObject.sellerId() == authentication.name or hasRole('OPS')")
public SellerPayoutView payout(String payoutId) { ... }
```
The method still ran — never use it for methods with side effects.

### `@PreFilter` · `@PostFilter` ⚠️
Filter collection arguments or results by an expression. Filtering in memory after loading is inefficient and leak-prone; scope the query instead (Chapter 17).

### `@Secured` ⚠️ · `@RolesAllowed` ⚠️
Role lists without expressions (`@Secured` is Spring's, `@RolesAllowed` is Jakarta's). They work, but `@PreAuthorize` is the more flexible default.

```java title="Role-only check (snippet)"
@Secured("ROLE_OPS")
public void forceCancel(String orderRef) { ... }
```

### `@AuthenticationPrincipal` ✅
Injects the principal into controller methods (see [Web Layer](web.md)). `expression` can extract a claim.

```java title="Claim extraction (snippet)"
@GetMapping("/api/v1/me/tenant")
String tenant(@AuthenticationPrincipal(expression = "claims['tenant_id']") String tenantId) { return tenantId; }
```

### `@CurrentSecurityContext` ✅
Injects the `SecurityContext` or an expression over it.

## Security testing (`spring-security-test`)

### `@WithMockUser` ✅
Runs a test as a mock user with given roles/authorities.

```java title="CartControllerSecurityTest.java"
@WebMvcTest(CartController.class)
@Import(SecurityConfig.class)
class CartControllerSecurityTest {

    @Test
    @WithMockUser(username = "cust-42", roles = "CUSTOMER")
    void customerCanReadOwnCart() throws Exception { ... }

    @Test
    void anonymousIsRejected() throws Exception { ... }         // expect 401
}
```

### `@WithUserDetails` · `@WithAnonymousUser` · `@WithSecurityContext` ✅
Load a user from a `UserDetailsService`; run anonymously; build custom security contexts via a factory (useful for JWT-shaped principals). For JWT resource servers, the `jwt()` request post-processor is usually simpler than annotations (Chapter 18).

---

[:material-arrow-left: Data & Transactions](data.md) · [Async, Messaging & Resilience :material-arrow-right:](async-messaging.md)
