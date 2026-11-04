# 14 · Multimodality: Images, Audio & Moderation

**Why:** real assistants receive photos ("is this the right charger?"), voice notes, and need to generate
images or speech. Spring AI exposes each modality with the same portable style.

| Capability | Interface | Example providers |
|---|---|---|
| Image / PDF / audio **input** to chat | `UserMessage` + `Media` | OpenAI, Anthropic, Gemini, Bedrock, Ollama (vision models) |
| Image **generation** | `ImageModel` | OpenAI, Stability AI, Gemini |
| Speech-to-text | `TranscriptionModel` | OpenAI |
| Text-to-speech | `TextToSpeechModel` | OpenAI, ElevenLabs |
| Content moderation | `ModerationModel` | OpenAI, Mistral |

## 14.1 Images (and documents) as input

```java
String answer = chat.prompt()
        .user(u -> u.text("Which product is this, and is it damaged?")
                    .media(MimeTypeUtils.IMAGE_JPEG, new FileSystemResource("upload/1234.jpg")))
        .call()
        .content();
```

From a multipart upload:

```java
@PostMapping(value = "/api/assistant/photo", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
DamageAssessment assess(@RequestPart MultipartFile photo, @RequestPart String question) throws IOException {
    if (photo.getSize() > 5_000_000) throw new PayloadTooLargeException();
    MimeType type = MimeType.valueOf(Objects.requireNonNull(photo.getContentType()));
    if (!Set.of(MimeTypeUtils.IMAGE_JPEG, MimeTypeUtils.IMAGE_PNG).contains(type)) throw new UnsupportedMediaTypeException();

    return chat.prompt()
            .system("You assess product photos for return requests. Be factual; say 'unclear' if unsure.")
            .user(u -> u.text(question).media(type, new ByteArrayResource(photo.getBytes())))
            .call()
            .entity(DamageAssessment.class);
}

record DamageAssessment(boolean damageVisible, String description, Confidence confidence) {}
enum Confidence { HIGH, MEDIUM, LOW, UNCLEAR }
```

Production notes:

- **Validate type and size** before sending. Images cost many tokens (scaled by resolution); resize
  large uploads server-side.
- Use the model's assessment as **input to a human or rule-based decision**, never as the final decision
  on refunds.
- Some providers accept PDFs and audio as `Media` too; check the provider's supported MIME types.
- Images in prompts can carry **prompt-injection text** (instructions written in the picture). The same
  rules apply as for any untrusted input ([Security](19-security.md)).

## 14.2 Image generation

```java
@Service
class BannerService {
    private final ImageModel imageModel;

    BannerService(ImageModel imageModel) { this.imageModel = imageModel; }

    String generateBanner(String campaign) {
        ImageResponse response = imageModel.call(new ImagePrompt(
                "A clean, bright e-commerce banner for a " + campaign + " sale, no text, flat illustration",
                OpenAiImageOptions.builder()
                        .model("gpt-image-1")
                        .width(1536).height(1024)
                        .quality("high")
                        .n(1)
                        .build()));
        Image image = response.getResult().getOutput();
        return image.getUrl() != null ? image.getUrl() : image.getB64Json();
    }
}
```

```yaml
spring.ai.model.image: openai      # enable the image model auto-configuration
spring.ai.openai.image.model: gpt-image-1
```

Store generated images in your own object storage (provider URLs expire), record the prompt and model
for audit, and keep a human approval step for anything published.

## 14.3 Speech-to-text (transcription)

```java
@Service
class VoiceNoteService {
    private final TranscriptionModel transcriptionModel;

    VoiceNoteService(TranscriptionModel transcriptionModel) { this.transcriptionModel = transcriptionModel; }

    String transcribe(Resource audio) {
        return transcriptionModel.transcribe(audio);       // convenience method
    }

    String transcribeWithOptions(Resource audio) {
        var options = OpenAiAudioTranscriptionOptions.builder()
                .language("en")
                .prompt("Product names: Trail Runner, AeroPod, KettlePro")   // spelling hints
                .temperature(0f)
                .build();
        return transcriptionModel.call(new AudioTranscriptionPrompt(audio, options)).getResult().getOutput();
    }
}
```

```yaml
spring.ai.model.audio.transcription: openai
spring.ai.openai.audio.transcription.model: gpt-4o-mini-transcribe
```

Pipeline for voice support: transcribe → (redact PII) → normal text assistant → optional text-to-speech.

## 14.4 Text-to-speech

```java
byte[] mp3 = textToSpeechModel.call("Your order has shipped and will arrive on Thursday.");

TextToSpeechResponse response = textToSpeechModel.call(new TextToSpeechPrompt(
        "Your order has shipped.",
        OpenAiAudioSpeechOptions.builder().voice("alloy").speed(1.0).build()));
byte[] audio = response.getResult().getOutput();
```

`StreamingTextToSpeechModel` streams audio chunks (`Flux<TextToSpeechResponse>`) for low-latency playback.

```yaml
spring.ai.model.audio.speech: openai
spring.ai.openai.audio.speech.model: gpt-4o-mini-tts
```

## 14.5 Moderation

Check user input (and optionally model output) for harmful content before processing:

```java
@Service
class ModerationGuard {
    private final ModerationModel moderationModel;

    ModerationGuard(ModerationModel moderationModel) { this.moderationModel = moderationModel; }

    boolean isAllowed(String text) {
        ModerationResponse response = moderationModel.call(new ModerationPrompt(text));
        return response.getResult().getOutput().getResults().stream().noneMatch(ModerationResult::isFlagged);
    }
}
```

`ModerationResult` also exposes `getCategories()` (hate, harassment, self-harm, sexual, violence, …) and
`getCategoryScores()` so you can apply your own thresholds and route self-harm signals to a human
process. Wrap it in an advisor to apply it to every request ([Advisors](07-advisors.md)).

## 14.6 Multimodal embeddings

Some providers embed images and text into the same vector space (`spring.ai.model.embedding.multimodal`,
`DocumentEmbeddingModel`), enabling "search products by photo". Store image vectors with product ids in a
vector store and query with the uploaded photo's embedding.

## Common mistakes

| Mistake | Fix |
|---|---|
| Sending 12 MB photos | Validate size and resize |
| Using the vision answer to approve refunds | Human or rules decide; the model assists |
| Linking to provider image URLs | Copy to your own storage; URLs expire |
| No language hint for transcription | Set language and vocabulary prompt |
| Moderation only on input | Also moderate generated output that's published |

## Checkpoint

- [ ] A photo upload returns a typed assessment
- [ ] A voice note is transcribed and answered
- [ ] Input passes a moderation check before reaching the assistant

Next: [15 · Model Context Protocol](15-mcp.md)
