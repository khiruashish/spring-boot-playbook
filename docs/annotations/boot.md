# Spring Boot Annotations

Application bootstrap, configuration properties, auto-configuration and conditions. Deep dive: Chapters 05, 06, 29, 41.

## Application

### `@SpringBootApplication` ✅
`@SpringBootConfiguration` + `@EnableAutoConfiguration` + `@ComponentScan` of the annotated class's package and below.

```java title="OrderApplication.java"
package in.grocery.order;

@SpringBootApplication
@ConfigurationPropertiesScan
public class OrderApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}
```
Pitfall: place it in the root package — classes in sibling packages are not scanned.

### `@SpringBootConfiguration` ✅
A `@Configuration` marking the primary configuration; test slices use it to find the application. Normally only through `@SpringBootApplication`.

### `@EnableAutoConfiguration` ✅
Imports auto-configurations listed in `AutoConfiguration.imports`. Use `exclude` to drop one.

```java title="Excluding an auto-configuration (snippet)"
@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)   // a service with no database
public class NotificationApplication { ... }
```

### `@ImportAutoConfiguration` ✅
Imports specific auto-configurations — used by test slices and occasionally in tests.

```java title="Test importing one auto-configuration (snippet)"
@ImportAutoConfiguration(JacksonAutoConfiguration.class)
class MoneyJsonTest { ... }
```

### `@ServletComponentScan` ✅ (rare)
Registers classes annotated with `@WebServlet`, `@WebFilter`, `@WebListener`. In Spring apps, prefer filters as beans or `FilterRegistrationBean`.

## Configuration properties

### `@ConfigurationProperties` ✅
Binds a property prefix to a typed object — a record for immutability.

```java title="CartProperties.java"
@ConfigurationProperties("grocery.cart")
@Validated
public record CartProperties(
        @DefaultValue("50") @Min(1) @Max(200) int maxLines,
        @DefaultValue("20") @Min(1) int maxQuantityPerLine,
        @DefaultValue("24h") Duration abandonedAfter) {}
```
```yaml title="application.yml"
grocery:
  cart:
    max-lines: 50
    abandoned-after: 24h
```
Also usable on `@Bean` methods to bind third-party objects.

### `@EnableConfigurationProperties` ✅
Registers specific properties classes — the right choice inside auto-configurations and libraries.

```java title="GroceryWebAutoConfiguration.java"
@AutoConfiguration
@EnableConfigurationProperties(GroceryWebProperties.class)
public class GroceryWebAutoConfiguration { ... }
```

### `@ConfigurationPropertiesScan` ✅
Scans for `@ConfigurationProperties` classes in the application package — convenient in applications, not in libraries.

### `@DefaultValue` ✅
Default for a constructor-bound property; keeps defaults next to the field.

### `@ConstructorBinding` 📦
Only needed when a properties class has **several** constructors. Moved to `org.springframework.boot.context.properties.bind` in Boot 3; not needed on the class for a single constructor ([details](deprecated.md)).

### `@DurationUnit` · `@DataSizeUnit` · `@PeriodUnit` ✅
Units for bare numbers in configuration.

```java title="Units (snippet)"
public record OtpProperties(@DurationUnit(ChronoUnit.MINUTES) @DefaultValue("5") Duration ttl,
                            @DataSizeUnit(DataUnit.KILOBYTES) @DefaultValue("4") DataSize maxPayload) {}
```

### `@Name` ✅
Maps a property to a constructor parameter whose name is a Java keyword or differs.

### `@DeprecatedConfigurationProperty` ✅
Marks a getter/component as deprecated in generated metadata, with a replacement — IDEs then warn users (Chapter 41).

### `@NestedConfigurationProperty` ✅
Marks a field whose type isn't nested in the class as a nested group for metadata generation.

## Auto-configuration (for library and starter authors)

### `@AutoConfiguration` ✅
Declares an auto-configuration class (a non-proxying `@Configuration` with ordering attributes). Register it in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.

```java title="GroceryObservabilityAutoConfiguration.java"
@AutoConfiguration(after = MetricsAutoConfiguration.class)
@ConditionalOnClass(MeterRegistry.class)
public class GroceryObservabilityAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    MeterFilter groceryCardinalityGuard() {
        return MeterFilter.maximumAllowableTags("http.server.requests", "uri", 200, MeterFilter.deny());
    }
}
```

### `@AutoConfigureBefore` · `@AutoConfigureAfter` · `@AutoConfigureOrder` ✅
Ordering between auto-configurations. The `before`/`after` attributes on `@AutoConfiguration` are the modern form.

## Conditions

| Annotation | Registers the bean when… | Example |
|---|---|---|
| `@ConditionalOnClass` / `@ConditionalOnMissingClass` | a class is (not) on the classpath | Redis support only if Lettuce is present |
| `@ConditionalOnBean` / `@ConditionalOnMissingBean` | a bean does (not) exist — **the override mechanism** | Default `Clock` unless the app defines one |
| `@ConditionalOnSingleCandidate` | exactly one candidate (or a primary) exists | Wire the only `DataSource` |
| `@ConditionalOnProperty` | a property has a value | `grocery.tenancy.enabled=true` |
| `@ConditionalOnBooleanProperty` | a boolean property is true (newer Boot) — verify | Feature toggle |
| `@ConditionalOnResource` | a resource exists | A bundled model file |
| `@ConditionalOnWebApplication` / `@ConditionalOnNotWebApplication` | servlet/reactive/none | Filters only in web apps |
| `@ConditionalOnExpression` | a SpEL expression is true | Avoid — hard to debug |
| `@ConditionalOnJava` | a Java version range | Virtual-thread-specific beans |
| `@ConditionalOnCloudPlatform` | running on Kubernetes, etc. | Platform-specific defaults |
| `@ConditionalOnThreading` | platform or virtual threads active | Executor choice |

```java title="Conditions in practice (snippet)"
@Bean
@ConditionalOnMissingBean                                                   // the user's bean wins
@ConditionalOnProperty(prefix = "grocery.web", name = "enabled", havingValue = "true", matchIfMissing = true)
CorrelationIdFilter correlationIdFilter(GroceryWebProperties props) { ... }
```
Debug with `/actuator/conditions` or `--debug` (Chapter 41).

## Native images and AOT

### `@ImportRuntimeHints` ✅
Attaches a `RuntimeHintsRegistrar` declaring reflection/resource/serialization needs for GraalVM native images (Chapter 29).

```java title="NativeHints.java"
@Configuration(proxyBeanMethods = false)
@ImportRuntimeHints(OrderHints.class)
class NativeHints {}
```

### `@RegisterReflectionForBinding` ✅
Registers reflection hints for DTOs serialized reflectively.

```java title="Hints for event payloads (snippet)"
@RegisterReflectionForBinding({OrderPlacedEvent.class, PaymentCapturedEvent.class})
@Configuration(proxyBeanMethods = false)
class EventHints {}
```

### `@Reflective` ✅
Marks elements that need reflection at runtime in native images.

---

[:material-arrow-left: Core Container](core-container.md) · [Web Layer :material-arrow-right:](web.md)
