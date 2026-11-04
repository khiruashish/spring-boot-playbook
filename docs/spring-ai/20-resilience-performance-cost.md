# 20 · Resilience, Performance & Cost

**Why:** model providers have outages, rate limits and multi-second latencies, and every call costs money.
Production AI features need the same resilience engineering as any remote dependency, plus cost controls.

## 20.1 Failure modes

| Failure | Signal | Response |
|---|---|---|
| Rate limit | HTTP 429 | Retry with back-off (respect `Retry-After`); queue; reduce concurrency |
| Provider overload / 5xx | 500, 503, 529 | Retry a few times, then fallback model/provider |
| Timeout | No response in N s | Fail fast; fallback; tell the user |
| Bad request / auth | 400, 401, 403 | Don't retry; alert |
| Context too long | 400 "context length" | Trim memory/context; don't retry blindly |
| Content filtered | Provider refusal | Show a policy message |
| Malformed output | Parse failure | `validateSchema()` retry; fallback |

Spring AI classifies errors as `TransientAiException` (retryable) or `NonTransientAiException`.

## 20.2 Retries (built in)

```yaml
spring:
  ai:
    retry:
      max-attempts: 3                 # default 10: far too many for interactive traffic
      backoff:
        initial-interval: 1s          # default 2s
        multiplier: 2                 # default 5
        max-interval: 8s              # default 3m
      on-client-errors: false         # don't retry 4xx
      exclude-on-http-codes: [400, 401, 403, 404]
      on-http-codes: [429, 500, 502, 503, 504]
```

!!! warning "Double retries"
    The OpenAI and Anthropic SDK-based clients have their own `max-retries` setting
    (`spring.ai.openai.max-retries`, `spring.ai.anthropic.max-retries`). Make sure the two layers don't
    multiply (3 × 3 = 9 attempts). Pick one layer for retries.

For batch/background jobs (ingestion, enrichment) a longer retry policy is fine; for user-facing
endpoints, keep total worst-case time under your SLO.

## 20.3 Timeouts

```yaml
spring:
  ai:
    openai:
      timeout: 30s
    anthropic:
      timeout: 45s
```

Also put an **overall deadline** on the request (streaming: `.timeout(...)`; blocking: an async boundary
or Resilience4j `TimeLimiter`), because retries × timeout can exceed what the user will wait.

## 20.4 Circuit breaker and fallback model

With Resilience4j annotations (via Spring Cloud Circuit Breaker or Resilience4j's own Spring Boot
integration; pick the release line that supports your Boot 4 version):

```java
@Service
class ResilientAssistant {

    private final ChatClient primary;     // e.g. hosted large model
    private final ChatClient fallback;    // e.g. cheaper model from another provider, or self-hosted

    ResilientAssistant(@Qualifier("primaryClient") ChatClient primary,
                       @Qualifier("fallbackClient") ChatClient fallback) {
        this.primary = primary;
        this.fallback = fallback;
    }

    @CircuitBreaker(name = "llm-primary", fallbackMethod = "askFallback")
    public String ask(String conversationId, String question) {
        return primary.prompt().user(question)
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
                .call().content();
    }

    String askFallback(String conversationId, String question, Throwable t) {
        return fallback.prompt().user(question)
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
                .call().content();
    }
}
```

```yaml
resilience4j.circuitbreaker.instances.llm-primary:
  sliding-window-size: 50
  failure-rate-threshold: 50
  slow-call-duration-threshold: 20s
  slow-call-rate-threshold: 50
  wait-duration-in-open-state: 30s
```

Final fallback when every model is down: a static message with a link to help articles or a human
channel. Degrade, don't crash.

## 20.5 Rate limits and concurrency

- Know your provider limits (requests/min and tokens/min per model).
- Bound concurrency per provider with a `Bulkhead` or semaphore so a traffic spike becomes queueing, not
  a wall of 429s.
- Separate keys/projects for interactive traffic and batch jobs so ingestion can't starve users.

## 20.6 Latency engineering

| Technique | Gain |
|---|---|
| **Stream** responses | Perceived latency from seconds to ~0.5 s ([Streaming](06-streaming.md)) |
| Smaller/faster model for simple tasks | 2–10× faster |
| Fewer round trips (fewer RAG transformers, `returnDirect` tools) | Each removed call saves ~0.5–2 s |
| Shorter prompts and contexts (topK, memory window) | Faster first token |
| Parallel independent calls (virtual threads) | Wall-clock = slowest call, not the sum |
| Lower `maxTokens` / ask for concise answers | Output time is linear in tokens |
| Regional endpoints close to your servers | Network latency |
| Semantic cache for repeated questions | ~ms instead of seconds |
| Precompute (batch summaries, descriptions) | Zero request-time model calls |

## 20.7 Cost model

```text
monthly cost ≈ requests × (avg input tokens × input price + avg output tokens × output price)
             + embeddings + images/audio + evaluation runs
```

Input tokens usually dominate in RAG/chat apps because of system prompt + history + context on every turn.

## 20.8 Cost levers (biggest first)

| Lever | Typical saving |
|---|---|
| **Model routing**: cheap model for classification/extraction/simple Q&A; big model only when needed | 50–90% |
| **Don't call the model**: rules, search or templates for questions that don't need generation | 100% of those calls |
| **Prompt caching** for the stable prefix (system prompt, tools, documents) | Large reductions on cached input tokens |
| **Semantic cache** for repeated questions | 100% on hits |
| Trim context: memory window, topK, compact tool results | 20–60% of input |
| `maxTokens` and "be concise" | Output cost |
| Batch/offline jobs (precompute summaries, provider batch APIs) | Lower prices, no request-time cost |
| Self-hosted models for high-volume simple tasks | Infra cost instead of per-token |

## 20.9 Prompt caching

Providers cache a **stable prompt prefix** and bill cached input tokens at a large discount. To benefit:

1. Put stable content first: system prompt → tool definitions → static documents → (then) history → user message.
2. Don't put timestamps, user names or request ids at the start of the system prompt.
3. Check `Usage.getCacheReadInputTokens()` / `getCacheWriteInputTokens()` and the
   `gen_ai.usage.cache_read.input_tokens` attribute to verify hits.

OpenAI caches long prefixes automatically. Anthropic needs explicit cache breakpoints, configured in Spring AI:

```yaml
spring:
  ai:
    anthropic:
      chat:
        cache-options:
          strategy: system_and_tools      # none | system_only | tools_only | system_and_tools | conversation_history
```

## 20.10 Semantic cache

If many users ask the same thing in different words ("return policy?", "how do returns work"), answer from
a cache keyed by meaning:

```xml
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-redis-semantic-cache</artifactId>
</dependency>
```

```java
@Bean
SemanticCache semanticCache(JedisPooled jedis, EmbeddingModel embeddingModel) {
    return DefaultSemanticCache.builder()
            .jedisClient(jedis)
            .embeddingModel(embeddingModel)
            .similarityThreshold(0.95)          // be strict: wrong cache hits are wrong answers
            .build();
}

@Bean
ChatClient faqClient(ChatClient.Builder builder, SemanticCache cache, Advisor ragAdvisor) {
    return builder
            .defaultAdvisors(SemanticCacheAdvisor.builder().cache(cache).build(), ragAdvisor)
            .build();
}
```

!!! danger "Never cache personalised answers"
    Only cache answers that are the same for everyone (FAQ/policy). Answers using memory, tools or
    per-user data must bypass the cache, or include tenant/user scope in the key. Expire entries when the
    underlying documents change.

## 20.11 Token budgets

Enforce budgets at several levels: per request (`maxTokens`, input size limit), per user per day
([budget advisor](07-advisors.md#76-writing-an-advisor-calladvisor-around)), per tenant per month (plan
limits), and per environment (provider spend caps + alerts).

## 20.12 Load testing

Load-test with a **mock model server** (WireMock returning realistic latencies and token counts) to test
your own capacity (threads, connection pools, DB, vector store), then a short, low-volume test against the
real provider to validate rate limits. Never run a full load test against a paid API by accident.

## Common mistakes

| Mistake | Fix |
|---|---|
| Default retry (10 attempts, up to 3 min back-off) on a user endpoint | 2–3 attempts, short back-off |
| SDK retries + Spring retries | One layer |
| No fallback | Fallback model and a static message |
| Big model for everything | Route by task |
| Dynamic data at the start of the prompt | Stable prefix for caching |
| Caching personalised answers | Cache only shared FAQ answers |

## Checkpoint

- [ ] Retries and timeouts tuned so worst case < your SLO
- [ ] A circuit breaker switches to a fallback model
- [ ] Cost per feature is measured and routing uses a cheap model where evaluation allows
- [ ] Prompt caching hits are visible in usage metrics

Next: [21 · Production Deployment](21-production-deployment.md)
