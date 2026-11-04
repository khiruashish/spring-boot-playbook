# 10 · Embeddings

**Why:** embeddings turn text into vectors so you can search by *meaning*. They are the foundation of RAG,
semantic search, deduplication, recommendations and semantic caching.

## 10.1 The API

```java
@Service
class EmbeddingDemo {
    private final EmbeddingModel embeddingModel;      // auto-configured by the provider starter

    EmbeddingDemo(EmbeddingModel embeddingModel) { this.embeddingModel = embeddingModel; }

    void demo() {
        float[] one = embeddingModel.embed("How do I return an item?");
        List<float[]> many = embeddingModel.embed(List.of("refund policy", "shipping times"));
        int dims = embeddingModel.dimensions();                    // e.g. 1536

        EmbeddingResponse response = embeddingModel.embedForResponse(List.of("refund policy"));
        Usage usage = response.getMetadata().getUsage();           // tokens billed
    }
}
```

| Method | Use |
|---|---|
| `embed(String)` | One text → `float[]` |
| `embed(List<String>)` | Batch: one API call for many texts (cheaper, faster) |
| `embed(Document)` | Embeds a `Document`'s content (respecting its metadata mode) |
| `call(EmbeddingRequest)` | Full control: options per request |
| `dimensions()` | Vector length; must match the vector store column |

## 10.2 Configuration

```yaml
spring:
  ai:
    model:
      embedding: openai                  # or ollama, transformers, google-genai, bedrock, mistral ...
    openai:
      embedding:
        model: text-embedding-3-small
        dimensions: 1536                 # some models support shorter vectors (cheaper storage)
        metadata-mode: embed             # which Document metadata is included when embedding
```

Local embeddings without any server: `spring-ai-starter-model-transformers` runs an ONNX sentence-transformer
model in-process. Good for tests and for data that must not leave your network.

## 10.3 Similarity

```java
double similarity = SimpleVectorStore.cosineSimilarity(
        embeddingModel.embed("How do I return an item?"),
        embeddingModel.embed("What is your refund policy?"));   // ≈ 0.8–0.9 for most models
```

| Metric | Notes |
|---|---|
| **Cosine similarity** | Default for text; direction only |
| Dot product | Equals cosine for normalised vectors (most providers normalise) |
| Euclidean distance | Less common for text |

Scores are **model-specific**: a threshold of 0.75 for one model means nothing for another. Calibrate
thresholds with your own evaluation set.

## 10.4 Choosing an embedding model

| Criterion | Guidance |
|---|---|
| Quality | Benchmark on *your* queries, not leaderboards alone |
| Dimensions | More = more storage and slower search; 768–1536 is typical |
| Max input tokens | Chunks must fit (often 512–8192 tokens) |
| Language | Multilingual models for multilingual content |
| Cost & hosting | Hosted per-token pricing vs self-hosted (Ollama, ONNX) |
| **Stability** | Changing the model means **re-embedding everything** |

!!! warning "Embedding model changes are migrations"
    Vectors from different models are not comparable. Switching models (or even dimensions) requires
    re-embedding the whole corpus into a new table/index and switching over. Version your index (e.g. table
    `vector_store_v2`) and keep the model name in configuration and document metadata.

## 10.5 Batching

Vector stores embed documents in batches using a `BatchingStrategy`. The default
`TokenCountBatchingStrategy` packs documents into batches that fit the model's input token limit (with a
reserve). Customise when your provider has different limits:

```java
@Bean
BatchingStrategy batchingStrategy() {
    return new TokenCountBatchingStrategy(EncodingType.CL100K_BASE, 8000, 0.1);
}
```

## 10.6 What to embed

- Embed the **text that will be searched**, plus metadata that helps meaning (title, section heading).
  `MetadataMode.EMBED` controls which metadata is included.
- Don't embed boilerplate (navigation, footers, legal disclaimers repeated on every page).
- For products, embed a synthesised description ("Trail Runner 2: waterproof trail running shoe, 240 g,
  recycled sole") rather than raw JSON.

## 10.7 Uses beyond RAG

| Use | How |
|---|---|
| Semantic search | Embed query → nearest products |
| Deduplication | Pairs above a similarity threshold are duplicates |
| Clustering / topics | Cluster support tickets by vector |
| Recommendations | "Similar products" = nearest neighbours of a product vector |
| Semantic cache | Reuse answers for near-identical questions ([page 20](20-resilience-performance-cost.md)) |
| Routing | Compare a query with example vectors per intent |

## 10.8 Cost and performance

- Embedding is cheap per token but large corpora add up: embed **once**, store, and re-embed only changed
  documents (content hash; see [ETL](12-etl-pipeline.md#126-idempotent-re-indexing)).
- Embed queries at request time (one small call); cache embeddings of popular queries if needed.
- Batch ingestion off the request path (scheduled jobs, message consumers).

## Common mistakes

| Mistake | Fix |
|---|---|
| Comparing vectors from different models | One model per index; re-embed on change |
| Hard-coded similarity thresholds from blog posts | Calibrate on your data |
| Embedding one text per API call in a loop | Batch |
| Vector column dimension ≠ model dimensions | Set both explicitly |

## Checkpoint

- [ ] You can embed a batch and print dimensions and token usage
- [ ] You measured similarity for similar vs unrelated sentences with your model
- [ ] The embedding model name is in configuration and recorded with the index

Next: [11 · Vector Stores](11-vector-stores.md)
