# 6 · Streaming Responses

**Why:** a 6-second answer feels broken; the same answer streaming word by word from 400 ms feels fast.
Streaming improves **perceived** latency (time to first token) and lets users cancel early.

## 6.1 The API

```java
Flux<String> tokens = chat.prompt().user(question).stream().content();

Flux<ChatResponse> responses = chat.prompt().user(question).stream().chatResponse();     // with metadata

Flux<ChatClientResponse> full = chat.prompt().user(question).stream().chatClientResponse(); // with advisor context
```

`stream()` returns a cold `Flux`: nothing is sent to the model until something subscribes.

## 6.2 Server-Sent Events from Spring MVC

Spring MVC can return a `Flux` directly (Reactor is on the classpath with Spring AI):

```java
@RestController
@RequestMapping("/api/assistant")
class StreamingController {

    private final ChatClient chat;

    StreamingController(ChatClient supportClient) { this.chat = supportClient; }

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    Flux<ServerSentEvent<String>> stream(@RequestParam @Size(max = 2000) String q,
                                         @RequestParam String conversationId) {
        return chat.prompt()
                .user(q)
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
                .stream()
                .content()
                .map(token -> ServerSentEvent.builder(token).event("token").build())
                .concatWithValues(ServerSentEvent.builder("").event("done").build())
                .onErrorResume(e -> Flux.just(
                        ServerSentEvent.builder("The assistant is unavailable.").event("error").build()));
    }
}
```

Same code works in **WebFlux**. MVC holds an async request open without blocking a thread; with virtual
threads enabled you can also use `SseEmitter` if you prefer an imperative style.

## 6.3 Consuming the stream in a browser (Angular / plain JS)

```javascript
const source = new EventSource(`/api/assistant/stream?q=${encodeURIComponent(q)}&conversationId=${id}`);
source.addEventListener('token', e => { answerEl.textContent += e.data; });
source.addEventListener('done',  () => source.close());
source.addEventListener('error', () => source.close());
```

`EventSource` only supports GET without custom headers. For POST bodies or `Authorization` headers, use
`fetch()` with a `ReadableStream` reader, or a small SSE client library.

## 6.4 Cancellation saves money

When the client disconnects, the `Flux` is cancelled and Spring AI stops reading from the provider. Make
sure nothing in your pipeline (e.g. `.cache()`, `.share()` or a blocking collect) keeps the subscription
alive after the client leaves. Also apply a server-side timeout:

```java
.stream().content()
.timeout(Duration.ofSeconds(60))
```

## 6.5 Token usage while streaming

Providers send usage in the final chunk (OpenAI requires `stream_options.include_usage`, which Spring AI can
set via `streamOptions`). Aggregate from `chatResponse()`:

```java
Flux<ChatResponse> flux = chat.prompt().user(q).stream().chatResponse();

flux.doOnNext(r -> {
        Usage u = r.getMetadata().getUsage();
        if (u != null && u.getTotalTokens() != null && u.getTotalTokens() > 0) {
            meterRegistry.counter("shopassist.tokens", "type", "total").increment(u.getTotalTokens());
        }
    })
    .mapNotNull(r -> r.getResult() == null ? null : r.getResult().getOutput().getText());
```

Observability metrics (`gen_ai.client.token.usage`) are recorded for streaming calls too
([Observability](17-observability.md)).

## 6.6 Streaming with memory, RAG and tools

Advisors implement `StreamAdvisor` as well as `CallAdvisor`, so memory, RAG and the tool loop work with
streaming. Memory advisors aggregate the streamed chunks and save the **complete** assistant message when the
stream finishes (`ChatClientMessageAggregator`). If the client cancels mid-stream, the partial answer may not
be stored; design the UI to tolerate that.

## 6.7 When *not* to stream

| Situation | Why |
|---|---|
| Structured output (`entity`) | You need the complete JSON; schema validation doesn't support streaming |
| Server-to-server / batch jobs | No human waiting; simpler code with `call()` |
| Output must be checked before showing (moderation, PII) | Buffer, check, then return, or check in chunks and accept the complexity |

## Common mistakes

| Mistake | Fix |
|---|---|
| `.collectList().block()` inside a request thread | Return the `Flux` |
| No timeout | `.timeout(...)` |
| Showing raw errors mid-stream | `onErrorResume` → a friendly `error` event |
| Expecting usage on every chunk | Usage arrives in the final chunk |
| Streaming structured output | Use `call().entity(...)` |

## Checkpoint

- [ ] An SSE endpoint streams tokens and ends with a `done` event
- [ ] Closing the browser tab stops the provider call
- [ ] Token usage is recorded for streamed answers

Next: [7 · Advisors](07-advisors.md)
