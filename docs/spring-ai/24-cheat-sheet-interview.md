# 24 · Cheat Sheet & Interview Questions

## 24.1 API cheat sheet

```java
// ChatClient basics
ChatClient chat = builder.defaultSystem("...").defaultOptions(ChatOptions.builder().temperature(0.2).maxTokens(600)).build();
String text          = chat.prompt().user(q).call().content();
ChatResponse resp    = chat.prompt().user(q).call().chatResponse();           // usage, finish reason
T entity             = chat.prompt().user(q).call().entity(T.class);
List<T> list         = chat.prompt().user(q).call().entity(new ParameterizedTypeReference<List<T>>() {});
T strict             = chat.prompt().user(q).call().entity(T.class, s -> s.useProviderStructuredOutput().validateSchema());
Flux<String> stream  = chat.prompt().user(q).stream().content();

// Templates
chat.prompt().user(u -> u.text("Hello {name}").param("name", n)).call().content();
chat.prompt().system(new ClassPathResource("prompts/system.st")).user(q).call().content();

// Memory
MessageChatMemoryAdvisor.builder(chatMemory).build();
chat.prompt().advisors(a -> a.param(ChatMemory.CONVERSATION_ID, id)).user(q).call().content();

// RAG
QuestionAnswerAdvisor.builder(vectorStore).searchRequest(SearchRequest.builder().topK(4).similarityThreshold(0.5).build()).build();
RetrievalAugmentationAdvisor.builder().documentRetriever(VectorStoreDocumentRetriever.builder().vectorStore(vs).build()).build();

// Tools
chat.prompt().tools(new MyTools()).toolContext(Map.of("userId", uid)).user(q).call().content();
FunctionToolCallback.builder("name", fn).description("...").inputType(Req.class).build();

// Embeddings & vector store
float[] v = embeddingModel.embed("text");
vectorStore.add(docs);
vectorStore.similaritySearch(SearchRequest.builder().query(q).topK(4).filterExpression("tenant == 'acme'").build());
vectorStore.delete("source == 'faq.md'");

// ETL
vectorStore.accept(TokenTextSplitter.builder().withChunkSize(500).build().apply(new TikaDocumentReader(resource).get()));

// Other modalities
imageModel.call(new ImagePrompt("...", OpenAiImageOptions.builder().width(1024).height(1024).build()));
transcriptionModel.transcribe(audioResource);
textToSpeechModel.call("text");
moderationModel.call(new ModerationPrompt(text));
```

## 24.2 Properties cheat sheet

| Property | Default | Purpose |
|---|---|---|
| `spring.ai.model.chat` / `.embedding` / `.image` / `.audio.transcription` / `.audio.speech` / `.moderation` | provider on classpath | Choose provider per model type (`none` disables) |
| `spring.ai.<provider>.api-key`, `.base-url`, `.timeout`, `.max-retries` | — | Connection |
| `spring.ai.<provider>.chat.model`, `.temperature`, `.max-tokens` / `.max-completion-tokens` | provider default | Chat options (2.0: no `.options.`) |
| `spring.ai.<provider>.embedding.model`, `.dimensions` | — | Embedding options |
| `spring.ai.chat.client.enabled` | `true` | Auto-configure `ChatClient.Builder` |
| `spring.ai.chat.client.tool-calling.enabled` / `.advisor-order` | `true` / `HIGHEST_PRECEDENCE+300` | Auto-register `ToolCallingAdvisor` |
| `spring.ai.chat.client.observations.log-prompt` / `.log-completion` | `false` | ChatClient content in observations |
| `spring.ai.chat.observations.log-prompt` / `.log-completion` / `.include-error-logging` | `false` | Model-level content in observations |
| `spring.ai.tools.throw-exception-on-error` | `false` | Propagate tool exceptions instead of returning them to the model |
| `spring.ai.tools.limits.max-total-tool-calls` | `150` | Tool calls per turn |
| `spring.ai.tools.limits.max-calls-per-tool-default` / `.max-calls-per-tool.<name>` | `40` | Per-tool limit |
| `spring.ai.tools.limits.on-limit-exceeded` | `throw` | or `return_error_response` |
| `spring.ai.tools.resolution.fallback.enabled` | `false` | Resolve tools not attached to the request |
| `spring.ai.tools.observations.include-content` | `false` | Tool args/results in observations |
| `spring.ai.retry.max-attempts` | `10` | Retries for model calls |
| `spring.ai.retry.backoff.initial-interval` / `.multiplier` / `.max-interval` | `2s` / `5` / `3m` | Back-off |
| `spring.ai.retry.on-client-errors` / `.exclude-on-http-codes` / `.on-http-codes` | `false` / `[]` / `[]` | Which errors retry |
| `spring.ai.vectorstore.pgvector.initialize-schema` | `false` | Create table/extension |
| `spring.ai.vectorstore.pgvector.dimensions` / `.distance-type` / `.index-type` / `.id-type` | model / `cosine_distance` / `hnsw` / `uuid` | Vector table |
| `spring.ai.vectorstore.pgvector.table-name` / `.schema-name` | `vector_store` / `public` | Location |
| `spring.ai.chat.memory.repository.jdbc.initialize-schema` | `embedded` | Chat memory table |
| `spring.ai.mcp.server.name` / `.version` / `.type` / `.protocol` / `.stdio` | `mcp-server` / `1.0.0` / `SYNC` / `STREAMABLE` / `false` | MCP server |
| `spring.ai.mcp.server.streamable-http.mcp-endpoint` | `/mcp` | MCP endpoint |
| `spring.ai.mcp.client.streamable-http.connections.<name>.url` / `.endpoint` | — | MCP client connections |
| `spring.ai.mcp.client.stdio.connections.<name>.command` / `.args` | — | Local MCP servers |
| `spring.ai.ollama.base-url` / `.init.pull-model-strategy` | `http://localhost:11434` / `never` | Ollama |

## 24.3 Decision cheat sheet

| Question | Answer |
|---|---|
| `ChatModel` or `ChatClient`? | `ChatClient`, unless writing infrastructure or controlling the tool loop |
| RAG or tools? | RAG for slow-changing documents; tools for live/per-user data |
| RAG or fine-tuning? | RAG for knowledge; fine-tuning only for style/format at scale |
| Which vector store? | pgvector if you run Postgres; search engine for hybrid at scale |
| Stream or not? | Stream for humans reading text; `call()` for structured output and server-to-server |
| Agent or workflow? | Workflow unless the steps genuinely can't be known in advance |
| Big or small model? | Smallest that passes your evaluation; route by task |
| Memory size? | 10–20 messages; summarise or semantic recall beyond that |

## 24.4 Interview questions & answers

### Fundamentals (0–3 years)

**1. What is Spring AI?**
A Spring project that provides portable abstractions (`ChatModel`, `ChatClient`, `EmbeddingModel`,
`VectorStore`, tools, advisors) and Boot auto-configuration for AI providers, so you can build AI features
the Spring way and switch providers with configuration.

**2. Difference between `ChatModel` and `ChatClient`?**
`ChatModel` is the low-level provider abstraction (`Prompt` in, `ChatResponse` out). `ChatClient` is a
fluent API on top with advisors, tools, memory, structured output and streaming. In 2.0 the tool loop
lives in an advisor, so only `ChatClient` runs it automatically.

**3. What is a token and why does it matter?**
A chunk of text (~4 characters). Pricing, context limits and latency are all measured in tokens; input and
output are billed separately.

**4. What does temperature do?**
Controls randomness. Low (0–0.3) for extraction, classification and support; higher for creative text.

**5. How do you get a Java object from a model?**
`call().entity(MyRecord.class)`: Spring AI generates a JSON schema, adds format instructions (or uses
native structured output), and deserialises with Jackson. Validate the result afterwards.

**6. Why is the `ChatClient.Builder` a prototype bean?**
So each service can customise its own builder (system prompt, advisors) without affecting others; the
built `ChatClient` is immutable and reused.

**7. How do you stream a response to a browser?**
`stream().content()` returns `Flux<String>`; return it from a controller as `text/event-stream`
(Server-Sent Events).

**8. How do you keep API keys safe?**
Environment variables/secret managers, never in code or prompts; per-environment keys; provider spend limits.

### Intermediate (3–6 years)

**9. Explain RAG and its two phases.**
Ingestion: read → split → embed → store in a vector store with metadata. Query time: embed the question,
retrieve the top-K similar chunks (filtered), add them to the prompt, generate a grounded answer.

**10. What are embeddings and cosine similarity?**
Vectors representing meaning; cosine similarity measures the angle between them, so semantically similar
texts score close to 1.

**11. How do you choose chunk size?**
Start around 300–800 tokens, respect structure (headings, paragraphs, one product per doc), and tune using
retrieval evaluation (recall@K).

**12. What are advisors? Give examples.**
Interceptors around `ChatClient` calls, ordered by `getOrder()`: memory, RAG, tool calling, logging, safe
guard, structured-output validation, and your own (PII redaction, budgets).

**13. How does chat memory work, and what are its risks?**
A memory advisor loads the last N messages for a conversation id and saves the new turn. Risks: token
growth, cross-user leakage (unowned ids), personal data retention.

**14. How does tool calling work?**
Tool definitions (name, description, JSON schema) are sent with the prompt; the model returns tool-call
requests; `ToolCallingAdvisor` executes them and sends results back until the model gives a final answer.

**15. How do you pass the current user to a tool safely?**
`ToolContext` (or the security context), which is never sent to the model. Never accept identity as a
tool argument.

**16. What is `returnDirect`?**
The tool result is returned to the caller without another model call, which saves latency/cost and
guarantees exact output.

**17. How do metadata filters work in vector search?**
Portable expressions (`tenant == 'acme' && lang in ['en','de']`) or `FilterExpressionBuilder`, translated to
the store's native filter; used for tenancy, permissions, language, freshness.

**18. How do you handle provider failures?**
Classify transient vs permanent; tuned retries with back-off; timeouts; circuit breaker; fallback model;
static fallback message; map to `ProblemDetail`.

### Senior (6–10 years)

**19. How do you test a non-deterministic feature?**
Unit-test code around the model with a mocked `ChatModel`; integration-test retrieval with Testcontainers;
evaluate behaviour on a golden dataset with property checks and LLM judges (`RelevancyEvaluator`,
`FactCheckingEvaluator`), gating releases on pass rates.

**20. How do you defend against prompt injection?**
Assume it will succeed and limit the blast radius: least-privilege tools, authorization in tools and
retrieval, confirmation for side effects, delimiting untrusted data, input/output screening, monitoring,
and injection cases in evaluation.

**21. How do you control cost?**
Measure tokens × price per feature; route to smaller models; prompt caching (stable prefix); semantic
cache for shared answers; trim context; cap output; budgets and rate limits; precompute offline.

**22. What changes when you swap the embedding model?**
All vectors must be regenerated; build a new index, backfill, evaluate, switch with a flag, keep the old
index for rollback.

**23. Explain modular RAG in Spring AI.**
`RetrievalAugmentationAdvisor` composes query transformers (rewrite, compress, translate), expanders
(multi-query), retrievers, joiners, post-processors (rerank, budget) and an augmenter (with an empty-context
policy).

**24. How would you make an agent safe for production?**
Clear scope, least-privilege tools, tool-call limits, token/time budgets, human confirmation for side
effects, handoff tool, full tracing, scenario-based evaluation.

**25. What do you monitor for an AI feature?**
Latency (p95 by model), tokens and cost by feature/model, error/retry rates, tool calls and limit hits,
retrieval empty rate, truncation (`finishReason=LENGTH`), user feedback, escalation rate.

**26. When do you use MCP instead of `@Tool`?**
When tools should be shared across applications/agents/IDEs or owned by another team: MCP exposes them
over a standard protocol; `@Tool` is in-process and app-specific.

### Architect / lead (10+ years)

**27. Where should an LLM never be the authority?**
Money, permissions, legal/medical decisions, inventory and order state: anything with financial or safety
impact. The model suggests; deterministic systems and humans decide.

**28. How do you roll out a prompt or model change?**
Treat it as a release: PR + evaluation, feature flag/canary, compare quality/cost/latency metrics, quick
rollback via configuration.

**29. How do you design multi-tenant RAG?**
Tenant id in every document's metadata; mandatory server-side filter wrapper; optionally separate
tables/indexes for large or sensitive tenants; per-tenant budgets; evaluation includes cross-tenant attempts.

**30. Self-hosted vs hosted models?**
Hosted: best models, no ops, per-token cost, data leaves your network (mitigated by enterprise terms and
regions). Self-hosted: data control and predictable cost at high volume, but GPUs, capacity planning and
usually weaker models. Many teams mix: hosted for hard tasks, self-hosted for high-volume simple ones.

### Scenario questions

**31. Users report the assistant "forgot" the conversation after a deploy.**
In-memory chat memory lost on restart, or conversation ids not persisted client-side. Use a JDBC/Redis
repository and server-issued conversation ids.

**32. Monthly bill doubled with flat traffic.**
Check tokens per request: memory window growth, larger topK, new tools (definitions are tokens), a model
change, tool loops, or prompt caching broken by dynamic content at the start of the prompt.

**33. The bot answered with another customer's order.**
A tool took the customer id from model arguments or skipped the ownership check. Fix: identity from
`ToolContext`/security context, ownership query, regression test and evaluation case; treat as a security
incident.

**34. RAG says "I don't know" to questions the docs answer.**
Inspect retrieved chunks: threshold too high, wrong filter, poor chunking, or vocabulary mismatch
(add hybrid search or query rewriting). Measure recall@K.

**35. Latency p95 is 9 s.**
Profile the trace: multiple model calls (query transformers, tool loops), large contexts, a slow model,
retries. Stream, trim context, use a faster model for sub-steps, parallelise, cache.

**36. How would you build "chat with our product catalog"?**
Ingest product descriptions (one product per document, with category/price/brand metadata) for semantic
search; live stock and price through tools; structured product cards via structured output; tenant/locale
filters; evaluation on real queries; semantic cache for popular questions.

**37. A model release changed answer style and broke your parser.**
Use structured output with schema validation, pin model versions, and run evaluation before switching
versions.

**38. The provider is down for an hour.**
The circuit breaker opens → fallback model/provider; if none, a clear degraded-mode message and human
contact; alerts fire; no readiness failures, because health checks don't depend on the provider.

**39. Legal asks where customer data goes.**
Show the inventory: which features send which fields to which provider/region, retention settings, DPAs,
redaction, and where memory and logs are stored and for how long.

**40. Design a review-summarisation feature for 1M products.**
Batch offline: parallel chunked summarisation with a small model, store summaries, refresh on new reviews
(event-driven) with a debounce, show the cached summary on product pages. Zero request-time model calls.

## 24.5 Coding exercise

Build `POST /api/assistant/classify` that classifies a support message into an enum category with a
confidence and a one-sentence reason, using structured output at temperature 0; reject inputs over 2000
characters with RFC 9457 `ProblemDetail`; record token usage as a metric; and ship:

- a unit test with a mocked `ChatModel` asserting the prompt and parsing,
- a validation test for oversized input,
- an evaluation test over 20 labelled messages requiring ≥ 90% accuracy.

Back to the [Spring AI overview](index.md).
