# 17 · Observability

**Why:** AI features fail in new ways: slow providers, cost spikes, tool loops, quality drift after a model
or prompt change. You need to see **latency, tokens, cost, errors and quality**, per feature, per model, and
trace a single conversation across advisors, tools and vector searches.

## 17.1 What Spring AI instruments (Micrometer Observation API)

| Observation | Name | Key tags (low-cardinality) |
|---|---|---|
| ChatClient call | `spring.ai.chat.client` | `spring.ai.kind`, stream, advisors, tool names |
| Advisor | `spring.ai.advisor` | advisor name and order |
| Model call (chat, embedding, image, audio) | `gen_ai.client.operation` | `gen_ai.operation.name`, `gen_ai.system` (provider), `gen_ai.request.model`, `gen_ai.response.model` |
| Tool call | `spring.ai.tool` | `spring.ai.tool.definition.name` |
| Vector store | `db.vector.client.operation` | store type, operation (add/query/delete) |

Metrics derived from them (OpenTelemetry GenAI semantic conventions):

| Metric | Meaning |
|---|---|
| `gen_ai.client.operation` (timer; exported as `gen_ai_client_operation_seconds_*` in Prometheus) | Model call latency per provider/model/operation |
| `gen_ai.client.token.usage` | Tokens, tagged `gen_ai.token.type` = `input` / `output` / `total` |
| `spring.ai.chat.client`, `spring.ai.advisor`, `spring.ai.tool`, `db.vector.client.operation` timers | Latency of each layer |

Span attributes also include request options (temperature, max tokens), finish reasons, response id, and
usage including cache read/write tokens (`gen_ai.usage.cache_read.input_tokens`).

## 17.2 Step 1: enable metrics and tracing

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
<!-- tracing via OpenTelemetry (Boot 4) -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-opentelemetry</artifactId>
</dependency>
```

```yaml
management:
  endpoints.web.exposure.include: health,info,prometheus
  tracing.sampling.probability: 0.1          # sample in prod; 1.0 in dev
  opentelemetry.tracing.export.otlp.endpoint: http://otel-collector:4318/v1/traces
  metrics.tags:
    application: shopassist
```

Now every request produces a trace like:

```text
http POST /api/assistant/ask                         2.41 s
└─ spring.ai.chat.client                              2.38 s
   ├─ spring.ai.advisor  MessageChatMemoryAdvisor      0.01 s
   ├─ spring.ai.advisor  ToolCallingAdvisor            2.35 s
   │  ├─ gen_ai.client.operation chat gpt-4o-mini       0.92 s   tokens in=1840 out=36
   │  ├─ spring.ai.tool getOrderStatus                  0.04 s
   │  │  └─ http GET order-service/orders/1042           0.03 s
   │  └─ gen_ai.client.operation chat gpt-4o-mini       1.31 s   tokens in=1930 out=88
   └─ spring.ai.advisor  QuestionAnswerAdvisor
      └─ db.vector.client.operation query pgvector     0.02 s
```

## 17.3 Logging prompt and completion content: carefully

Content is **not** recorded by default, because prompts contain personal data. You can enable it per layer:

```yaml
spring:
  ai:
    chat:
      client:
        observations:
          log-prompt: false        # ChatClient-level prompt
          log-completion: false
      observations:
        log-prompt: false          # model-level prompt (Spring AI logs a warning when enabled)
        log-completion: false
        include-error-logging: true
    tools:
      observations:
        include-content: false     # tool arguments & results
```

Enable content only in dev/test, or in prod with redaction, short retention and restricted access to the
tracing backend.

## 17.4 Step 2: cost tracking

Tokens × price = cost. Record cost as your own metric with low-cardinality tags (feature, model), not per
user:

```java
@Component
class AiCostMeter {
    private final MeterRegistry registry;
    private final Map<String, ModelPrice> prices;   // from configuration: per-million-token prices in micro-cents

    AiCostMeter(MeterRegistry registry, AiPricingProperties pricing) {
        this.registry = registry;
        this.prices = pricing.models();
    }

    void record(String feature, ChatResponse response) {
        var md = response.getMetadata();
        var usage = md.getUsage();
        var price = prices.get(md.getModel());
        if (price == null || usage == null) return;

        long microCents = price.inputPerMillion() * nz(usage.getPromptTokens()) / 1_000_000
                        + price.outputPerMillion() * nz(usage.getCompletionTokens()) / 1_000_000;

        registry.counter("shopassist.ai.cost", "feature", feature, "model", md.getModel())
                .increment(microCents);
    }

    private static long nz(Integer v) { return v == null ? 0 : v; }
}
```

Better: do it once in an advisor ([Advisors](07-advisors.md)) that tags the cost with a `feature` advisor
parameter.

## 17.5 Step 3: business and quality signals

Technical metrics don't tell you whether answers are good. Add:

| Signal | How |
|---|---|
| 👍/👎 feedback | Endpoint storing feedback with the response id and trace id |
| "I don't know" rate | Count answers matching your fallback phrase |
| Escalation to human rate | Count handoff tool calls |
| Tool error rate | Tool observation errors |
| `finishReason = LENGTH` rate | Answers truncated by `maxTokens` |
| Retrieval empty rate | RAG returned no documents |
| Guardrail blocks | Count of moderation/injection blocks |

## 17.6 Dashboards

A Grafana dashboard per AI feature:

| Panel | PromQL (example) |
|---|---|
| Model latency p95 by model | `histogram_quantile(0.95, sum by (le, gen_ai_request_model) (rate(gen_ai_client_operation_seconds_bucket[5m])))` |
| Tokens per minute by type | `sum by (gen_ai_token_type) (rate(gen_ai_client_token_usage_total[1m]))` |
| Cost per hour by feature | `sum by (feature) (rate(shopassist_ai_cost_total[1h])) * 3600` |
| Error rate | `sum(rate(gen_ai_client_operation_seconds_count{error!="none"}[5m])) / sum(rate(gen_ai_client_operation_seconds_count[5m]))` |
| Tool calls by name | `sum by (spring_ai_tool_definition_name) (rate(spring_ai_tool_seconds_count[5m]))` |
| Vector query latency | `histogram_quantile(0.95, sum by (le) (rate(db_vector_client_operation_seconds_bucket[5m])))` |

Exact metric names depend on your registry's naming convention; check `/actuator/prometheus` for yours.

## 17.7 Alerts

| Alert | Condition |
|---|---|
| Provider degraded | p95 model latency > 2× baseline for 10 min, or error rate > 5% |
| Cost spike | Hourly cost > 2× the 7-day same-hour average |
| Token explosion | Tokens per request p95 doubles (often a prompt/memory bug) |
| Tool loop | `ToolCallLimitExceededException` count > 0 |
| Quality drop | 👎 rate or "I don't know" rate up significantly after a deploy |

## 17.8 Correlating everything

- Put the **trace id** in API responses (header) and in feedback records.
- Log the **prompt version**, model and conversation id on each request (MDC / observation tags, keeping
  high-cardinality values out of metrics).
- Keep **evaluation results** per release so you can compare quality across deploys.

## Common mistakes

| Mistake | Fix |
|---|---|
| Logging full prompts in prod logs | Off by default; redact if needed |
| User id as a metric tag | High cardinality: put it in traces/logs, not metrics |
| Only technical metrics | Add feedback and quality signals |
| No cost metric | Tokens × price per feature/model |
| Tracing sampled at 100% in prod | Sample; keep errors |

## Checkpoint

- [ ] Prometheus shows `gen_ai.client.token.usage` and model latency
- [ ] A single request is visible as a trace with model, tool and vector spans
- [ ] Cost per feature is on a dashboard with an alert

Next: [18 · Testing & Evaluation](18-testing-evaluation.md)
