# Coding Interview: 12 Spring Boot Problems, Solved & Tested

Spring Boot coding rounds hand you a half-built service and ask you to **add the production behaviour**: validation and
proper error responses, pagination, idempotent POSTs, rate limiting, transactions that roll back correctly, a custom
starter, validated configuration, caching, an HTTP client, method security. Every problem here is solved in one
**Spring Boot 4.0** application in
[`coding-interview/`](https://github.com/khiruashish/spring-boot-playbook/tree/main/coding-interview) (Java 21) and
**proven by tests**: `MockMvc`, `ApplicationContextRunner`, `@RestClientTest` with `MockRestServiceServer`, and
`@WithMockUser`. That's 54 tests in all, run by CI on every change. The "output" on each page is that problem's real test report.

Two of the traps on these pages were hit for real while building the solutions, and they're kept as lessons. A catch-all
`@ExceptionHandler` turning a 403 into a 500 (problem 12), and reading a public field through a cache proxy (problem 10).

Each page follows the same structure:

1. **Problem**: the statement as an interviewer would give it.
2. **Key idea**: the shape of the solution before any code, with a diagram.
3. **Solution**: the complete, runnable code (included from the repository, so it is exactly what CI ran).
4. **Walkthrough**: the important lines and *why* they are written that way.
5. **Complexity**: time and space for each approach.
6. **Run it**: the command and its real output.
7. **Common mistakes** and **follow-up questions** with answers.

## Problem map

| # | Problem | What it tests | Level | Difficulty |
|---|---|---|---|---|
| 1 | [REST CRUD with Validation](01-rest-crud-validation.md) | `@Valid` record DTOs, 201 + `Location`, 404, idempotent DELETE | <span class="level l1">L1</span> | ★☆☆ |
| 2 | [Global Error Handling with ProblemDetail](02-global-error-handling.md) | `@RestControllerAdvice`, `ResponseEntityExceptionHandler`, RFC 9457, no leaks | <span class="level l2">L2</span> | ★★☆ |
| 3 | [Custom Cross-Field Validator](03-custom-validator.md) | `@Constraint`, `ConstraintValidator`, class-level constraints, property nodes | <span class="level l2">L2</span> | ★★☆ |
| 4 | [Pagination & Safe Sorting](04-pagination-sorting.md) | Page metadata, max page size, sort whitelist, built-in method validation | <span class="level l2">L2</span> | ★★☆ |
| 5 | [Idempotency-Key Servlet Filter](05-idempotency-filter.md) | `OncePerRequestFilter`, request body replay, response caching, 409 / 422 | <span class="level l3">L3</span> | ★★★ |
| 6 | [Rate Limiting with a HandlerInterceptor](06-rate-limit-interceptor.md) | Token bucket per client, 429 + `Retry-After`, injectable `Clock` | <span class="level l2">L2</span> | ★★☆ |
| 7 | [@Transactional: The Three Traps](07-transactional-pitfalls.md) | Rollback rules, self-invocation, `REQUIRES_NEW` audit | <span class="level l3">L3</span> | ★★★ |
| 8 | [Write a Custom Auto-Configuration (Starter)](08-custom-auto-configuration.md) | `@AutoConfiguration`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, `ApplicationContextRunner` | <span class="level l3">L3</span> | ★★★ |
| 9 | [Validated @ConfigurationProperties](09-validated-configuration-properties.md) | Immutable record binding, `@DefaultValue`, `Duration` parsing, fail-fast startup | <span class="level l2">L2</span> | ★★☆ |
| 10 | [Caching: @Cacheable, @CachePut, @CacheEvict](10-caching.md) | Read-through, write-through, eviction, `unless`, proxy pitfalls | <span class="level l2">L2</span> | ★★☆ |
| 11 | [RestClient with Error Mapping, Tested](11-restclient-testing.md) | `RestClient`, `onStatus`, URI templates, `@RestClientTest` + `MockRestServiceServer` | <span class="level l2">L2</span> | ★★☆ |
| 12 | [Method Security: Roles & Ownership](12-method-security.md) | `@PreAuthorize`, `@PostAuthorize`, SpEL on arguments/results, 401 vs 403 | <span class="level l3">L3</span> | ★★★ |

Levels: <span class="level l1">L1</span> 0–2 yrs · <span class="level l2">L2</span> 2–5 yrs · <span class="level l3">L3</span> 5–10 yrs · <span class="level l4">L4</span> 10+ yrs / architect.

## Which technique fits? (the interviewer's hidden question)

```mermaid
flowchart TD
    Q{What is the interviewer adding?}
    Q -->|Endpoint + input rules| A[Controller + Bean Validation #1 #3]
    Q -->|Consistent error JSON| B[RestControllerAdvice + ProblemDetail #2]
    Q -->|Big result sets| C[Pagination + sort whitelist #4]
    Q -->|Safe client retries| D[Servlet filter: Idempotency-Key #5]
    Q -->|Per-client throttling| E[HandlerInterceptor: token bucket #6]
    Q -->|All-or-nothing DB writes| F[@Transactional rules #7]
    Q -->|Reusable library| G[Auto-configuration + conditions #8]
    Q -->|Config that can't be wrong| H[@ConfigurationProperties + @Validated #9]
    Q -->|Slow lookups| I[@Cacheable / @CachePut / @CacheEvict #10]
    Q -->|Calling another service| J[RestClient + MockRestServiceServer #11]
    Q -->|Who may do what| K[@PreAuthorize / @PostAuthorize #12]
```

## How to answer a coding round

1. **Say which layer the behaviour belongs in**: filter (before Spring MVC), interceptor (around handlers), advice (errors), service (business rules, transactions, security).
2. **Write the test first** in the slice that fits: `MockMvc` for HTTP behaviour, `ApplicationContextRunner` for configuration, `@RestClientTest` for clients. Interviewers love seeing the test.
3. **Get the HTTP semantics right**: 201 + `Location`, 204, 400 vs 422, 409, 429 + `Retry-After`, 401 vs 403, `application/problem+json`.
4. **Explain the proxy**: `@Transactional`, `@Cacheable` and `@PreAuthorize` all work through proxies, which explains most of their pitfalls.
5. **Mention production hardening**: Redis instead of in-memory maps, Caffeine or Redis caches with TTLs, Resilience4j around clients, observability.

## Run every solution

```bash
coding-interview/run-tests.sh          # all 54 tests, writes outputs/
coding-interview/run-tests.sh --check  # what CI runs: fails on any failing test or changed report
```
