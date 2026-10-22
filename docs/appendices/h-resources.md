# Appendix H · Resources

Where to go next. Official documentation first, because it's authoritative and versioned; then books that shaped the handbook's thinking; then practice.

!!! tip "Prefer versioned official documentation"
    Spring projects publish reference documentation per version. When a chapter marks something **(verify)**, the reference guide for your exact version is the source of truth — not blog posts, and not this handbook.

## H.1 Official Spring documentation

| Resource | Use for | Chapters |
|---|---|---|
| Spring Boot Reference Guide | Configuration, auto-configuration, Actuator, testing, packaging | 05–07, 15, 27, 29, 41 |
| Spring Boot migration guides and release notes | What changed between versions | 42, App. E |
| Spring Framework Reference | Core container, AOP, transactions, MVC, WebFlux, REST clients, resilience | 02–04, 08, 16, 19, 26, 31 |
| Spring Security Reference | Filter chain, authorization, OAuth2 resource server/client, testing | 17, 18, 39 |
| Spring Authorization Server Reference | Issuing tokens, clients, key management | 18 |
| Spring Data (JPA, JDBC, Redis, MongoDB, R2DBC, Elasticsearch) References | Repositories, templates, mapping | 12, 13, 21, 22, 31 |
| Spring for Apache Kafka Reference | Listeners, error handling, transactions, testing | 23 |
| Spring AMQP / Spring Pulsar References | RabbitMQ and Pulsar integration | 24 |
| Spring Batch / Spring Integration References | Batch jobs, EIP flows | 33 |
| Spring for GraphQL / Spring gRPC References | GraphQL and gRPC | 32 |
| Spring Modulith Reference | Modules, events, documentation | 37 |
| Spring Cloud documentation | Gateway, LoadBalancer, release trains | 35 |
| Spring AI Reference | Chat, RAG, tools, observability | 40 |
| Spring support policy page | Support windows per release line | 42 |

## H.2 Platform and ecosystem documentation

| Resource | Chapters |
|---|---|
| OpenJDK JEPs (virtual threads, scoped values, structured concurrency, AOT cache) | 25, 29 |
| Hibernate ORM User Guide | 13, 38 |
| PostgreSQL documentation (EXPLAIN, indexes, locking, RLS, logical replication) | 12, 14, 34, 36, 38 |
| Flyway / Liquibase documentation | 14 |
| Apache Kafka documentation | 23 |
| RabbitMQ documentation (quorum queues, dead lettering) | 24 |
| Redis documentation | 21, 22 |
| OpenSearch / Elasticsearch documentation | 22 |
| Micrometer and OpenTelemetry documentation | 27 |
| Resilience4j documentation | 26 |
| Testcontainers, WireMock, Pact, ArchUnit, PIT documentation | 15, 28 |
| Kubernetes, Helm, KEDA, Argo Rollouts documentation | 30 |
| GraalVM Native Image and Cloud Native Buildpacks documentation | 29 |
| Debezium documentation | 36 |
| OpenRewrite recipe catalog | 42 |

## H.3 Standards and specifications

| Standard | Topic | Chapters |
|---|---|---|
| RFC 9110 | HTTP semantics | 08, 20 |
| RFC 9457 | Problem details for HTTP APIs | 10 |
| RFC 8594 / RFC 9745 | Sunset and Deprecation headers | 20 |
| RFC 6749 / 6750 / 7636 / 9068 | OAuth 2.0, bearer tokens, PKCE, JWT access tokens | 18 |
| OpenAPI Specification 3.1 | API description | 20 |
| Jakarta Bean Validation | Validation | 09 |
| W3C Trace Context | Distributed tracing propagation | 27 |
| Reactive Streams | Backpressure protocol | 31 |
| OWASP Top 10, ASVS, Top 10 for LLM Applications | Security | 39, 40 |
| PCI DSS guidance on scope and tokenization | Payments | 39 |
| DPDP Act 2023 and RBI directions (with counsel) | Indian data protection and payment data | 39 |

## H.4 Books

| Book | Why it matters here |
|---|---|
| *Designing Data-Intensive Applications* — Martin Kleppmann | Consistency, replication, stream processing (Ch 22, 23, 36) |
| *Release It!* — Michael Nygard | Stability patterns and anti-patterns (Ch 26) |
| *Building Microservices* and *Monolith to Microservices* — Sam Newman | Boundaries and extraction (Ch 35) |
| *Microservices Patterns* — Chris Richardson | Sagas, outbox, CQRS (Ch 36) |
| *Domain-Driven Design* — Eric Evans; *Implementing DDD* — Vaughn Vernon | Contexts and aggregates (Ch 37) |
| *Get Your Hands Dirty on Clean Architecture* — Tom Hombergs | Hexagonal architecture in Spring (Ch 37) |
| *Java Concurrency in Practice* — Goetz et al. | Concurrency foundations (Ch 25) |
| *Systems Performance* — Brendan Gregg | Methodology, profiling (Ch 34) |
| *Site Reliability Engineering* and *The SRE Workbook* — Google | SLOs, alerting, incidents (Ch 27, 43) |
| *Accelerate* — Forsgren, Humble, Kim | DORA metrics (Ch 43) |
| *Working Effectively with Legacy Code* — Michael Feathers | Characterization tests, modernization (Ch 42) |
| *Enterprise Integration Patterns* — Hohpe and Woolf | Messaging vocabulary (Ch 24, 33) |
| *Staff Engineer* — Will Larson; *The Staff Engineer's Path* — Tanya Reilly | Senior technical leadership (Ch 43) |
| *Effective Java* — Joshua Bloch | Java fundamentals (Ch 01) |

## H.5 Source code worth reading

| Code | What you learn | Chapters |
|---|---|---|
| Spring Boot's `WebMvcAutoConfiguration`, `DataSourceAutoConfiguration` | How conditions and back-off work in practice | 05, 41 |
| `TransactionInterceptor` / `TransactionAspectSupport` | Exactly how `@Transactional` behaves | 16 |
| `DispatcherServlet` | The MVC request pipeline | 08 |
| `FilterChainProxy`, `AuthorizationFilter` | Spring Security internals | 17 |
| `CacheAspectSupport` | Caching semantics including `sync` | 21 |
| `KafkaMessageListenerContainer`, `DefaultErrorHandler` | Consumer loop and error handling | 23 |
| Spring PetClinic and the Spring guides | Idiomatic, current examples | all |

Reading framework source is the fastest route from B3 to B4: most "why does it behave like this?" questions have a twenty-line answer in the code.

## H.6 Practice

| Activity | Link to the handbook |
|---|---|
| Build the capstone milestones M1–M8 | Chapter 44 |
| Work through the coding exercises by band | Appendix B |
| Answer the interview bank aloud, one band above your level | Appendix A |
| Run a game day against your own services | Chapters 30, 44 |
| Write one ADR and one post-incident review per quarter | Chapter 43 |
| Upgrade a side project to each new Boot minor on release | Chapter 42 |
| Read one framework class a week | H.5 |

## H.7 Keeping this handbook current

| Task | Cadence |
|---|---|
| Re-verify items marked **(verify)** against new releases | Each Boot minor |
| Update Appendix E with new version differences | Each Boot major/minor |
| Add questions from real interviews to Appendix A | Ongoing |
| Add incidents' lessons to Appendix F | After each post-incident review |
| Rebuild with `mkdocs build --strict` | Every change |

---

[:material-arrow-left: G Glossary](g-glossary.md) · [Handbook home :material-arrow-right:](../index.md)
