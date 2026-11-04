# 23 · Migration: Spring AI 1.x → 2.0

Spring AI 2.0 (GA in June 2026; 2.0.2 at the time of writing) moves to the Spring Boot 4 generation and
cleans up several APIs. Upgrade **Spring Boot first** (see [Chapter 42 · Migration & Upgrade
Engineering](../part-3-enterprise/42-migration-upgrade.md)), then Spring AI.

!!! info "Scope of this list"
    The changes below were confirmed by reading the 2.0.2 source code. Always read the official upgrade
    notes for your exact versions too; milestones and point releases may add details.

## 23.1 Platform baseline

| Area | 1.x | 2.0 |
|---|---|---|
| Spring Boot | 3.4 / 3.5 | **4.0 / 4.1** (can't be used with Boot 3) |
| Spring Framework | 6.x | 7.x |
| Jakarta EE | 10 | 11 |
| Jackson | 2 (`com.fasterxml.jackson.databind`) | **3** (`tools.jackson.databind`, `JsonMapper`) |
| Null-safety | — | JSpecify annotations (`@Nullable`) |
| Java | 17+ | 17+ (21+ recommended) |

## 23.2 API and configuration changes

| Change | 1.x | 2.0 | Action |
|---|---|---|---|
| Per-request options | `.options(ChatOptions)` | `.options(ChatOptions.Builder)`; `defaultOptions(ChatOptions.Builder)` | Pass the builder (drop `.build()`) |
| Model properties | `spring.ai.openai.chat.options.model` | `spring.ai.openai.chat.model` (same for other providers) | Move keys up one level; old keys deprecated |
| Tool-calling loop | Inside `ChatModel` (internal tool execution) | `ToolCallingAdvisor`, auto-registered by `ChatClient` | Use `ChatClient`; with raw `ChatModel`, run `ToolCallingManager` yourself |
| Tool advisor name | `ToolCallAdvisor` (2.0 milestones) | `ToolCallingAdvisor` | Rename; old class deprecated |
| Disable auto tool advisor | — | `AdvisorParams.toolCallingAdvisorAutoRegister(false)` / `spring.ai.chat.client.tool-calling.enabled=false` | |
| Tool-call limits | — | `spring.ai.tools.limits.*` (default 40 per tool, 150 total) | Set tighter limits |
| Tools by bean name | Resolved via `ToolCallbackResolver` | Request-bound only; fallback resolution off by default (2.0.1+) | Register tools explicitly |
| Memory conversation id | Could default to a shared id | Required; missing id → `IllegalArgumentException` | Always pass `ChatMemory.CONVERSATION_ID` |
| `PromptChatMemoryAdvisor` | Available | Not present in 2.0.2 | Use `MessageChatMemoryAdvisor` |
| Structured output | Prompt-based conversion | Plus `useProviderStructuredOutput()`, `validateSchema()`, `StructuredOutputValidationAdvisor` | Opt in where supported |
| Vector store advisors module | `spring-ai-advisors-vector-store` | `spring-ai-vector-store-advisor` | Rename dependency |
| Azure OpenAI | `azure-openai` module | Removed; OpenAI starter (official OpenAI Java SDK) supports Microsoft Foundry/Azure | Switch starter and properties |
| OpenAI client | Spring `RestClient`-based | Official `openai-java` SDK underneath | Check custom HTTP customisations |
| MCP | Separate MCP projects/annotations | MCP annotations (`@McpTool`, …) in Spring AI core | Update imports to `org.springframework.ai.mcp.annotation` |
| New | — | `ToolSearchToolCallingAdvisor`, Redis `SemanticCacheAdvisor`, cache token usage in `Usage` | Optional |

## 23.3 Code examples

```java
// 1.x
chatClient.prompt()
        .options(OpenAiChatOptions.builder().temperature(0.2).build())
        .user(q).call().content();

// 2.0
chatClient.prompt()
        .options(OpenAiChatOptions.builder().temperature(0.2))
        .user(q).call().content();
```

```yaml
# 1.x
spring.ai.openai.chat.options.model: gpt-4o-mini
spring.ai.openai.chat.options.temperature: 0.2

# 2.0
spring.ai.openai.chat.model: gpt-4o-mini
spring.ai.openai.chat.temperature: 0.2
```

```java
// Jackson 3 in custom converters
import tools.jackson.databind.json.JsonMapper;     // was com.fasterxml.jackson.databind.ObjectMapper
var converter = new BeanOutputConverter<>(ProductInfo.class, JsonMapper.builder().build());
```

## 23.4 Step-by-step upgrade plan

1. **Get green on the latest 1.1.x** with no deprecation warnings.
2. **Upgrade to Spring Boot 4** (Jakarta EE 11, Jackson 3, Spring Security 7 changes). Fix compile errors.
3. **Bump the Spring AI BOM to 2.0.x.** Fix compile errors: options builders, renamed modules/classes,
   Jackson imports.
4. **Move properties** from `*.chat.options.*` to `*.chat.*`; run with
   `spring-boot-properties-migrator` temporarily to spot old keys.
5. **Tool calling**: if you used `ChatModel` directly with tools, add explicit `ToolCallingManager` loops;
   configure `spring.ai.tools.limits`.
6. **Memory**: make sure every call passes a conversation id.
7. **Run the full test + evaluation suite**; compare quality, latency and token usage with 1.x results.
8. Roll out gradually behind a flag or canary.

## Checkpoint

- [ ] App runs on Boot 4 + Spring AI 2.0 with no deprecated properties
- [ ] Evaluation scores equal or better than before the upgrade
- [ ] Tool limits and conversation ids verified

Next: [24 · Cheat Sheet & Interview Questions](24-cheat-sheet-interview.md)
