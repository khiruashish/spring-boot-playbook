# Appendix D · Properties Cheat Sheet

The configuration properties used across the handbook, grouped by area, with the **production value the platform uses** and the reason. Defaults are Boot's unless noted.

!!! warning "Verify names for your version"
    Property names occasionally change between Boot releases (the properties migrator reports them — Chapter 42). Values here are the platform's choices, not universal truths: derive yours from measurements (Chapter 34).

## D.1 Application and lifecycle

```yaml
spring:
  application:
    name: order-service                       # used in logs, metrics, tracing
  main:
    banner-mode: off
    lazy-initialization: false                # keep failures at startup (Ch 03)
  lifecycle:
    timeout-per-shutdown-phase: 25s           # < pod grace period (Ch 03, 30)
  threads:
    virtual:
      enabled: true                           # Java 21+; add bulkheads (Ch 25)
server:
  port: 8080
  shutdown: graceful                          # default since 3.4
  error:
    include-stacktrace: never                 # never leak internals (Ch 10, 39)
    include-message: never
  tomcat:
    max-http-form-post-size: 256KB
    connection-timeout: 5s
```

| Property | Platform value | Why | Ch |
|---|---|---|---|
| `spring.lifecycle.timeout-per-shutdown-phase` | 25s | Must fit inside `terminationGracePeriodSeconds` | 03, 30 |
| `spring.threads.virtual.enabled` | true | Blocking becomes cheap; downstream limits matter | 25 |
| `server.shutdown` | graceful | Drain in-flight requests | 03 |
| `server.error.include-*` | never | No stack traces or messages in responses | 10 |

## D.2 Configuration

```yaml
spring:
  config:
    import:
      - optional:file:/etc/grocery/application.yml          # ConfigMap (Ch 06, 30)
      - optional:configtree:/var/run/secrets/grocery/       # Secrets as files
  profiles:
    active: prod                                            # usually via env var
```

| Property | Note | Ch |
|---|---|---|
| `spring.config.import` | ConfigMap file + secret config tree | 06 |
| `spring.profiles.active` | Set by `SPRING_PROFILES_ACTIVE` | 06 |
| `spring.profiles.group.*` | Compose profiles (`prod: [prod-db, prod-kafka]`) | 06 |

## D.3 Logging

```yaml
logging:
  structured:
    format:
      console: ecs                              # JSON logs (Boot 3.4+) (Ch 07)
  level:
    root: info
    in.grocery: info
    org.hibernate.SQL: warn                     # never DEBUG in production
  pattern:
    correlation: "[${spring.application.name:},%X{traceId:-},%X{spanId:-}] "
```

## D.4 Web and JSON

```yaml
spring:
  mvc:
    problemdetails:
      enabled: true                             # RFC 9457 (Ch 10)
  jackson:
    default-property-inclusion: non_null
    serialization:
      write-dates-as-timestamps: false          # ISO-8601 (Ch 11)
    deserialization:
      fail-on-unknown-properties: false         # tolerant readers (Ch 20)
  servlet:
    multipart:
      max-file-size: 5MB                        # bounded uploads (Ch 39)
      max-request-size: 10MB
  data:
    web:
      pageable:
        max-page-size: 100                      # bounded pages (Ch 08, 20)
        default-page-size: 20
```

| Property | Platform value | Ch |
|---|---|---|
| `spring.mvc.problemdetails.enabled` | true | 10 |
| `spring.jackson.serialization.write-dates-as-timestamps` | false | 11 |
| `spring.jackson.deserialization.fail-on-unknown-properties` | false | 11, 20 |
| `spring.data.web.pageable.max-page-size` | 100 | 20 |

## D.5 HTTP clients

```yaml
spring:
  http:
    client:
      connect-timeout: 1s                       # Boot 3.4+ (Ch 19)
      read-timeout: 2s
      redirects: dont-follow                    # SSRF hygiene (Ch 39)
grocery:
  clients:
    pricing:
      base-url: http://pricing-service:8080
      read-timeout: 600ms                       # fits checkout budget (Ch 19, 34)
    inventory:
      base-url: http://inventory-service:8080
      read-timeout: 500ms
```

Boot 4 adds per-group HTTP service client properties (`spring.http.client.service.group.<name>.*`) — **verify** names.

## D.6 Data

```yaml
spring:
  datasource:
    url: jdbc:postgresql://orders-db-rw:5432/orders
    hikari:
      maximum-pool-size: 20                     # from Little's law + DB budget (Ch 12)
      minimum-idle: 20
      connection-timeout: 2s                    # fail fast on exhaustion
      max-lifetime: 30m                         # below DB/LB idle limits
      leak-detection-threshold: 20s
  jpa:
    open-in-view: false                         # always (Ch 13)
    hibernate:
      ddl-auto: validate                        # schema via Flyway only (Ch 14)
    properties:
      hibernate:
        jdbc.batch_size: 50
        order_inserts: true
        order_updates: true
        default_batch_fetch_size: 50            # softens N+1
        query.fail_on_pagination_over_collection_fetch: true
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: false
  transaction:
    default-timeout: 10s                        # bound long transactions (Ch 16)
```

| Property | Platform value | Why | Ch |
|---|---|---|---|
| `hikari.maximum-pool-size` | 20 | × pods × services must fit `max_connections` | 12, 30 |
| `hikari.connection-timeout` | 2s | Pool exhaustion becomes a fast, visible error | 12 |
| `jpa.open-in-view` | false | No lazy loading in the web layer | 13 |
| `hibernate.ddl-auto` | validate | Migrations own the schema | 14 |
| `hibernate.default_batch_fetch_size` | 50 | N+1 safety net, not a fix | 13 |
| `spring.transaction.default-timeout` | 10s | No unbounded transactions | 16 |

## D.7 Caching and Redis

```yaml
spring:
  data:
    redis:
      host: redis
      timeout: 200ms                            # a cache must be fast or skipped (Ch 21)
      lettuce:
        pool:
          max-active: 16
          max-wait: 100ms
  cache:
    type: redis
    redis:
      key-prefix: "grocery:v4:"                 # versioned per major (Ch 21, 42)
      time-to-live: 5m
      cache-null-values: true
      enable-statistics: true                   # cache metrics
    caffeine:
      spec: maximumSize=5000,expireAfterWrite=10m,recordStats
```

## D.8 Kafka

```yaml
spring:
  kafka:
    bootstrap-servers: kafka:9092
    producer:
      acks: all
      properties:
        enable.idempotence: true
        linger.ms: 10
        compression.type: lz4
    consumer:
      group-id: ${spring.application.name}
      auto-offset-reset: earliest
      enable-auto-commit: false
      max-poll-records: 100
      value-deserializer: org.springframework.kafka.support.serializer.ErrorHandlingDeserializer
      properties:
        spring.deserializer.value.delegate.class: org.springframework.kafka.support.serializer.JsonDeserializer
        spring.json.trusted.packages: in.grocery.*.events          # never "*" (Ch 23)
        partition.assignment.strategy: org.apache.kafka.clients.consumer.CooperativeStickyAssignor
        max.poll.interval.ms: 300000
    listener:
      ack-mode: batch
      concurrency: 3                            # ≤ partitions
      observation-enabled: true
    template:
      observation-enabled: true
    admin:
      auto-create: false                        # topics are infrastructure
```

## D.9 RabbitMQ

```yaml
spring:
  rabbitmq:
    publisher-confirm-type: correlated          # know it was stored (Ch 24)
    publisher-returns: true                     # know it was routable
    listener:
      simple:
        acknowledge-mode: auto
        prefetch: 20                            # 1–5 for slow tasks
        default-requeue-rejected: false         # no poison loops
        retry:
          enabled: true
          max-attempts: 2
```

## D.10 Task execution and scheduling

```yaml
spring:
  task:
    execution:
      pool:
        core-size: 8
        max-size: 32
        queue-capacity: 100                     # default is effectively unbounded (Ch 25)
      thread-name-prefix: grocery-task-
      shutdown:
        await-termination: true
        await-termination-period: 20s
    scheduling:
      pool:
        size: 4                                 # default is 1
      shutdown:
        await-termination: true
        await-termination-period: 20s
```

## D.11 Security

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://id.grocery.in
          audiences: grocery-api                # validate audience (Ch 18)
      client:
        registration:
          grocery-internal:
            authorization-grant-type: client_credentials
            client-id: ${ORDER_SERVICE_CLIENT_ID}
            client-secret: ${ORDER_SERVICE_CLIENT_SECRET}
            scope: pricing:read,inventory:write
        provider:
          grocery-internal:
            token-uri: https://id.grocery.in/oauth2/token
```

## D.12 Actuator and observability

```yaml
management:
  server:
    port: 9090                                  # never on the public ingress (Ch 17, 27)
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,loggers,startup
  endpoint:
    health:
      probes:
        enabled: true
      show-details: when-authorized
      group:
        readiness:
          include: readinessState, db
        liveness:
          include: livenessState                # never dependencies (Ch 30)
  metrics:
    tags:
      application: ${spring.application.name}
    distribution:
      percentiles-histogram:
        http.server.requests: true
  tracing:
    sampling:
      probability: 0.1                          # tail sampling in the collector (Ch 27)
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces
  observations:
    annotations:
      enabled: true
  info:
    git:
      mode: simple
```

## D.13 Resilience4j

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        sliding-window-type: TIME_BASED
        sliding-window-size: 60
        minimum-number-of-calls: 20
        failure-rate-threshold: 50
        slow-call-duration-threshold: 2s
        slow-call-rate-threshold: 60
        wait-duration-in-open-state: 20s
        permitted-number-of-calls-in-half-open-state: 5
        register-health-indicator: true
        ignore-exceptions:
          - in.grocery.platform.error.DomainException     # business errors never open breakers
  retry:
    configs:
      default:
        max-attempts: 2
        wait-duration: 100ms
        enable-exponential-backoff: true
        enable-randomized-wait: true
  bulkhead:
    configs:
      default:
        max-concurrent-calls: 50
        max-wait-duration: 50ms
```

## D.14 Batch, Quartz, Modulith

```yaml
spring:
  batch:
    jdbc:
      initialize-schema: never                  # schema via Flyway (Ch 33)
    job:
      enabled: false                            # never run jobs on startup
  quartz:
    job-store-type: jdbc
    jdbc:
      initialize-schema: never
    properties:
      org.quartz.jobStore.isClustered: true
  modulith:
    events:
      republish-outstanding-events-on-restart: true    # verify name (Ch 37)
```

## D.15 Messaging protocols, GraphQL, AI

```yaml
spring:
  graphql:
    graphiql:
      enabled: false                            # dev only (Ch 32)
    schema:
      introspection:
        enabled: false                          # production
  ai:
    anthropic:
      api-key: ${ANTHROPIC_API_KEY}
      chat:
        options:
          model: ${GROCERY_AI_MODEL}            # pinned (Ch 40)
          temperature: 0.2
          max-tokens: 800
```

## D.16 Platform properties (grocery starters)

| Property | Default | Purpose | Ch |
|---|---|---|---|
| `grocery.web.enabled` | true | Toggle the web starter | 41 |
| `grocery.web.correlation-header` | `X-Request-Id` | Correlation header name | 07, 41 |
| `grocery.web.error-type-base-uri` | `https://errors.grocery.in/` | Problem `type` base | 10 |
| `grocery.observability.max-uri-tag-values` | 200 | Cardinality guard | 27 |
| `grocery.tenancy.enabled` | true | Toggle tenancy | 38 |
| `grocery.tenancy.claim-name` | `tenant_id` | Token claim for the tenant | 38 |
| `grocery.tenancy.row-level-security` | false | Opt in after policies exist | 38 |
| `grocery.outbox.poll-interval` | 300ms | Relay cadence | 36 |
| `grocery.outbox.batch-size` | 200 | Relay batch | 36 |
| `grocery.ai.support.enabled` | false | Feature flag for AI features | 40 |

## D.17 Kubernetes-facing values (not Spring properties, but coupled)

| Setting | Platform value | Must be consistent with | Ch |
|---|---|---|---|
| `terminationGracePeriodSeconds` | 45 | preStop (5 s) + shutdown phase (25 s) + margin | 30 |
| `preStop` sleep | 5 s | Endpoint propagation | 30 |
| Memory limit | = request | `-XX:MaxRAMPercentage=70` | 29, 30 |
| CPU limit | none (latency-sensitive) | Throttling metrics | 30 |
| `startupProbe.failureThreshold × periodSeconds` | ≥ 2× measured startup | Startup budget | 29, 30 |
| HPA `maxReplicas` | from connection budget | `hikari.maximum-pool-size` | 12, 30 |
| KEDA `maxReplicaCount` (consumers) | = partitions | Topic partition count | 23, 30 |

---

[:material-arrow-left: C Annotation Cheat Sheet](c-annotation-cheat-sheet.md) · [E Boot 3 vs 4 Matrix :material-arrow-right:](e-boot-3-vs-4-matrix.md)
