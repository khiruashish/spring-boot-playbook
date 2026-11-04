# 2 · Project Setup & Providers

**Goal:** a Spring Boot 4 application that talks to a model, configured the way you'd configure it for
production: managed versions, externalised keys, explicit model choice, and a local model for development.

## 2.1 Version matrix

| Spring AI | Spring Boot | Java | Notes |
|---|---|---|---|
| **2.0.x** (2.0.2 latest stable) | **4.0.x / 4.1.x** | 17+ (21+ recommended) | Jackson 3, JSpecify null-safety, MCP in core |
| 2.1.x | 4.x | 17+ | Milestones/RC at the time of writing |
| 1.0.x / 1.1.x | 3.4 / 3.5 | 17+ | Maintenance line for Boot 3 apps |

!!! tip "Always import the BOM"
    Spring AI ships ~150 artifacts. Import `spring-ai-bom` once and never write a Spring AI version on an
    individual dependency again.

## 2.2 Step 1: create the project

Use [start.spring.io](https://start.spring.io) with Spring Boot 4.1.x, Java 21, and the dependencies *Spring
Web*, *Actuator*, *Validation*, and one AI model (e.g. *OpenAI* or *Ollama*). Or write the build yourself:

=== "Maven"

    ```xml
    <parent>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-parent</artifactId>
      <version>4.1.2</version>
    </parent>

    <properties>
      <java.version>21</java.version>
      <spring-ai.version>2.0.2</spring-ai.version>
    </properties>

    <dependencyManagement>
      <dependencies>
        <dependency>
          <groupId>org.springframework.ai</groupId>
          <artifactId>spring-ai-bom</artifactId>
          <version>${spring-ai.version}</version>
          <type>pom</type>
          <scope>import</scope>
        </dependency>
      </dependencies>
    </dependencyManagement>

    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webmvc</artifactId>
      </dependency>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
      </dependency>
      <!-- pick ONE chat provider to start -->
      <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-starter-model-openai</artifactId>
      </dependency>
    </dependencies>
    ```

=== "Gradle (Kotlin DSL)"

    ```kotlin
    plugins {
        java
        id("org.springframework.boot") version "4.1.2"
        id("io.spring.dependency-management") version "1.1.7"
    }

    java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }

    dependencyManagement {
        imports { mavenBom("org.springframework.ai:spring-ai-bom:2.0.2") }
    }

    dependencies {
        implementation("org.springframework.boot:spring-boot-starter-webmvc")
        implementation("org.springframework.boot:spring-boot-starter-actuator")
        implementation("org.springframework.ai:spring-ai-starter-model-openai")
        testImplementation("org.springframework.boot:spring-boot-starter-test")
    }
    ```

!!! note "Starter names"
    Since 1.0 GA the naming scheme is `spring-ai-starter-<kind>-<name>`, for example
    `spring-ai-starter-model-openai`, `spring-ai-starter-vector-store-pgvector`,
    `spring-ai-starter-mcp-server-webmvc`. The pre-1.0 names (`spring-ai-openai-spring-boot-starter`) no longer exist.

## 2.3 Step 2: choose a provider

| Provider | Starter | Chat | Embeddings | Images | Audio | Good for |
|---|---|---|---|---|---|---|
| OpenAI (and OpenAI-compatible endpoints, Microsoft Foundry, GitHub Models) | `spring-ai-starter-model-openai` | ✅ | ✅ | ✅ | ✅ (transcription, speech) | Broad features, moderation |
| Anthropic (Claude) | `spring-ai-starter-model-anthropic` | ✅ | — | — | — | Reasoning, long context, prompt caching |
| Google Gemini (Gen AI / Vertex) | `spring-ai-starter-model-google-genai` (+ `-embedding`, `-image`) | ✅ | ✅ | ✅ | — | Multimodal, GCP |
| Amazon Bedrock (Converse API) | `spring-ai-starter-model-bedrock-converse` | ✅ | ✅ (`spring-ai-starter-model-bedrock`) | — | — | AWS, data residency |
| Mistral AI | `spring-ai-starter-model-mistral-ai` | ✅ | ✅ | — | — | EU hosting |
| DeepSeek | `spring-ai-starter-model-deepseek` | ✅ | — | — | — | Cost |
| **Ollama** (local / self-hosted) | `spring-ai-starter-model-ollama` | ✅ | ✅ | — | — | Dev, tests, air-gapped, privacy |
| ONNX Transformers (in-process) | `spring-ai-starter-model-transformers` | — | ✅ | — | — | Local embeddings without a server |
| Stability AI | `spring-ai-starter-model-stability-ai` | — | — | ✅ | — | Image generation |
| ElevenLabs | `spring-ai-starter-model-elevenlabs` | — | — | — | ✅ (speech) | Voices |

!!! warning "Azure OpenAI in 2.0"
    The separate `azure-openai` module was dropped in 2.0. Use the **OpenAI** starter, which is built on
    the official OpenAI Java SDK and supports Microsoft Foundry / Azure endpoints through its connection
    properties (`microsoft-deployment-name`, `credential`, etc.).

## 2.4 Step 3: configure it

In 2.0, model options live **directly** under `spring.ai.<provider>.chat.*`. The old `.chat.options.*`
nesting still binds but is deprecated.

=== "OpenAI"

    ```yaml
    spring:
      ai:
        openai:
          api-key: ${OPENAI_API_KEY}        # never commit keys
          chat:
            model: gpt-4o-mini              # name the model explicitly
            temperature: 0.2
            max-completion-tokens: 800
          embedding:
            model: text-embedding-3-small
    ```

=== "Anthropic"

    ```yaml
    spring:
      ai:
        anthropic:
          api-key: ${ANTHROPIC_API_KEY}
          chat:
            model: claude-sonnet-4-5        # use the model id your account offers
            max-tokens: 1024
            temperature: 0.2
    ```

=== "Ollama (local)"

    ```yaml
    spring:
      ai:
        ollama:
          base-url: http://localhost:11434
          init:
            pull-model-strategy: when_missing   # dev only; NEVER in prod (default is never)
          chat:
            model: llama3.1
            temperature: 0.2
          embedding:
            model: nomic-embed-text
    ```

!!! tip "Which model name?"
    Model ids change often. Always set the model explicitly in configuration (not code), pin it per
    environment, and re-run your [evaluation suite](18-testing-evaluation.md) before changing it.

## 2.5 Step 4: the first call

```java
package com.example.shopassist;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ai")
class HelloAiController {

    private final ChatClient chatClient;

    HelloAiController(ChatClient.Builder builder) {          // auto-configured, prototype-scoped
        this.chatClient = builder
                .defaultSystem("You are ShopAssist, a concise assistant for an online store.")
                .build();
    }

    @GetMapping("/ask")
    String ask(@RequestParam String q) {
        return chatClient.prompt()
                .user(q)
                .call()
                .content();
    }
}
```

```bash
export OPENAI_API_KEY=sk-...
./mvnw spring-boot:run
curl "localhost:8080/api/ai/ask?q=Suggest%20a%20gift%20under%2050%20dollars"
```

What happened:

1. The starter auto-configured an `OpenAiChatModel` from your properties.
2. `ChatClientAutoConfiguration` exposed a **prototype** `ChatClient.Builder` wired to that model, with
   observations and the tool-calling advisor pre-registered.
3. You built an immutable, thread-safe `ChatClient` once, in the constructor, and reuse it.

## 2.6 Step 5: several providers in one app

When more than one model starter is on the classpath, Boot can't guess which `ChatModel` to inject. Use
the model selection properties to enable/disable each type, then build one `ChatClient` per model:

```yaml
spring:
  ai:
    model:
      chat: openai          # which provider auto-configures the ChatModel ("none" disables)
      embedding: ollama     # embeddings from a local model
      image: none
      audio:
        transcription: none
        speech: none
      moderation: none
```

When you genuinely need two chat models at once (e.g. a cheap model for classification and a strong one for
answers), disable the global `ChatClient.Builder` and create explicit clients:

```yaml
spring.ai.chat.client.enabled: false
```

```java
@Configuration
class ChatClientsConfig {

    @Bean
    ChatClient fastClient(OpenAiChatModel openAi) {
        return ChatClient.builder(openAi)
                .defaultOptions(OpenAiChatOptions.builder().model("gpt-4o-mini").temperature(0.0))
                .build();
    }

    @Bean
    ChatClient smartClient(AnthropicChatModel anthropic) {
        return ChatClient.create(anthropic);
    }
}
```

Inject with `@Qualifier("fastClient")` or by parameter name. See [ChatClient](03-chat-client.md#37-multiple-chatclients).

## 2.7 Step 6: a local model for development and tests

Run Ollama locally so development doesn't spend money or send data out:

```yaml
# compose.yaml (picked up by spring-boot-docker-compose in dev)
services:
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama:/root/.ollama"]
volumes:
  ollama: {}
```

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-docker-compose</artifactId>
  <scope>runtime</scope>
  <optional>true</optional>
</dependency>
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-spring-boot-docker-compose</artifactId>
  <scope>runtime</scope>
  <optional>true</optional>
</dependency>
```

`spring-ai-spring-boot-docker-compose` and `spring-ai-spring-boot-testcontainers` provide **service
connections** for Ollama, vector stores and other services, so the URL is wired automatically. Combine with
Spring profiles: `dev` → Ollama, `prod` → hosted provider.

## 2.8 Step 7: API keys and secrets

| Do | Don't |
|---|---|
| `${OPENAI_API_KEY}` from environment / Kubernetes Secret / Vault / AWS Secrets Manager | Commit keys in `application.yml` |
| Separate keys per environment and per service | Share one key across teams |
| Set provider-side spend limits and alerts | Rely only on your own code for cost control |
| Rotate keys; restrict them by project | Log request headers |

## 2.9 Step 8: retries and timeouts (do it now, not later)

Spring AI wraps model calls with Spring Retry using these defaults: `max-attempts: 10`, initial back-off
2 s, multiplier 5, max interval 3 minutes. **That can mean many minutes of waiting on a user request.**
Tighten it for interactive traffic:

```yaml
spring:
  ai:
    retry:
      max-attempts: 3
      backoff:
        initial-interval: 1s
        multiplier: 2
        max-interval: 10s
      on-client-errors: false        # don't retry 4xx (bad request, auth)
      exclude-on-http-codes: [401, 403, 400]
    openai:
      timeout: 30s                   # per-request timeout on the HTTP client
      max-retries: 0                 # avoid double retries (SDK + Spring AI)
```

Details in [Resilience, Performance & Cost](20-resilience-performance-cost.md).

## Common mistakes

| Mistake | Fix |
|---|---|
| Versions on individual Spring AI artifacts | Import `spring-ai-bom` |
| Old starter names from blog posts | Use `spring-ai-starter-model-*` |
| Model left to provider default | Set `spring.ai.<provider>.chat.model` explicitly |
| Building a `ChatClient` per request | Build once; `ChatClient` is immutable and thread-safe |
| Two model starters, `NoUniqueBeanDefinitionException` | `spring.ai.model.chat=<provider>` or explicit beans |
| Default retry settings on a user-facing endpoint | Reduce `spring.ai.retry.*` and set timeouts |

## Checkpoint

- [ ] App starts and `/api/ai/ask` returns an answer
- [ ] Key comes from an environment variable
- [ ] Model name and `max-tokens` are set in configuration
- [ ] A `dev` profile runs against local Ollama
- [ ] Retry and timeout are tightened

Next: [3 · ChatClient Deep Dive](03-chat-client.md)
