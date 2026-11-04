# 11 · Vector Stores

**Why:** a vector store keeps documents, their embeddings and metadata, and finds the nearest documents to
a query fast, filtered by metadata (tenant, language, category).

## 11.1 The `VectorStore` API

```java
public interface VectorStore extends DocumentWriter, VectorStoreRetriever {
    void add(List<Document> documents);                 // embeds + stores
    void delete(List<String> idList);
    void delete(Filter.Expression filterExpression);
    default void delete(String filterExpression) { ... }
    List<Document> similaritySearch(SearchRequest request);   // from VectorStoreRetriever
    default List<Document> similaritySearch(String query) { ... }
    default <T> Optional<T> getNativeClient() { ... }
}
```

A `Document` has an `id`, `text` (or `media`), `metadata` (`Map<String,Object>`) and, in search results, a
`score`.

```java
Document doc = Document.builder()
        .id("policy-returns-001")
        .text("You can return unworn items within 30 days for a full refund...")
        .metadata(Map.of("source", "returns-policy.md", "tenant", "acme", "lang", "en", "version", 3))
        .build();

vectorStore.add(List.of(doc));
```

## 11.2 Step 1: PGvector (recommended default)

If you already run PostgreSQL, pgvector avoids a new database:

```xml
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-starter-vector-store-pgvector</artifactId>
</dependency>
```

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/shopassist
    username: shopassist
    password: ${DB_PASSWORD}
  ai:
    vectorstore:
      pgvector:
        initialize-schema: false          # Flyway owns the schema in prod
        schema-name: public
        table-name: vector_store
        dimensions: 1536                  # MUST match the embedding model
        distance-type: cosine_distance    # cosine_distance | euclidean_distance | negative_inner_product
        index-type: hnsw                  # hnsw (default) | ivfflat | none
        max-document-batch-size: 10000
```

Flyway migration equivalent to what Spring AI would create:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS vector_store (
    id        uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    content   text,
    metadata  json,
    embedding vector(1536)
);
CREATE INDEX IF NOT EXISTS vector_store_embedding_idx
    ON vector_store USING HNSW (embedding vector_cosine_ops);
```

!!! warning "Document ids and the UUID column"
    With the default id type the `id` column is a UUID, so document ids must be UUIDs. Generate them
    deterministically from a natural key (`UUID.nameUUIDFromBytes(("returns-policy.md#3").getBytes())`) so
    re-ingesting the same chunk overwrites instead of duplicating. Alternatively set
    `spring.ai.vectorstore.pgvector.id-type: text` (also `integer`, `serial`, `bigserial`) and use readable ids.

Local development with Docker Compose or Testcontainers: image `pgvector/pgvector:pg17`.

## 11.3 Step 2: searching

```java
List<Document> results = vectorStore.similaritySearch(SearchRequest.builder()
        .query("Can I return opened headphones?")
        .topK(4)                                 // default 4
        .similarityThreshold(0.6)                // default 0.0 = accept all; calibrate!
        .filterExpression("tenant == 'acme' && lang == 'en'")
        .build());

results.forEach(d -> System.out.printf("%.2f %s%n", d.getScore(), d.getMetadata().get("source")));
```

## 11.4 Metadata filters

Portable filter expressions are translated to each store's native query language.

Text syntax:

```text
tenant == 'acme'
category in ['shoes', 'socks'] && price <= 10000
lang == 'en' && !(status == 'archived')
year >= 2025 || featured == true
brand nin ['Acme', 'Contoso']
discontinued_at == null             (isNull support depends on store)
```

Type-safe builder:

```java
var b = new FilterExpressionBuilder();
Filter.Expression filter = b.and(
        b.eq("tenant", tenantId),
        b.in("category", "shoes", "socks")).build();

vectorStore.similaritySearch(SearchRequest.builder().query(q).filterExpression(filter).build());
```

Operators: `eq ne gt gte lt lte in nin and or not group isNull isNotNull`.

!!! danger "Tenant isolation is a filter you must never forget"
    In a multi-tenant system every search **must** include the tenant (and visibility/ACL) filter, built
    server-side from the authenticated user, never from user input. Wrap the store in your own
    `TenantScopedRetriever` so it can't be forgotten.

## 11.5 Deleting and updating

```java
vectorStore.delete(List.of(docId));                          // by id
vectorStore.delete("source == 'returns-policy.md'");         // by filter: e.g. before re-ingesting a file
```

There is no in-place update: delete the old chunks of a source, then add the new ones (or rely on
deterministic ids).

## 11.6 Supported stores

| Store | Starter | Notes |
|---|---|---|
| **PostgreSQL / pgvector** | `spring-ai-starter-vector-store-pgvector` | Reuse Postgres; HNSW; SQL + vectors |
| Redis | `-vector-store-redis` | Low latency; also used for semantic cache |
| Elasticsearch | `-vector-store-elasticsearch` | Hybrid lexical + vector |
| OpenSearch / AWS OpenSearch | `-vector-store-opensearch`, `-vector-store-aws-opensearch` | Hybrid search on AWS |
| MongoDB Atlas | `-vector-store-mongodb-atlas` | Document DB + vectors |
| Pinecone, Qdrant, Weaviate, Milvus, Chroma, Typesense | `-vector-store-<name>` | Dedicated vector DBs |
| Cassandra, Couchbase, Neo4j, Oracle, MariaDB, GemFire, Azure AI Search | `-vector-store-<name>` | Existing platforms |
| Amazon S3 Vectors, Bedrock Knowledge Bases | `-vector-store-s3`, `-vector-store-bedrock-knowledgebase` | AWS-managed |
| `SimpleVectorStore` | in `spring-ai-vector-store` | In-memory; tests and demos only |

All implement the same `VectorStore` interface, so switching is mostly configuration.

## 11.7 Choosing a store

| If you… | Choose |
|---|---|
| Already run PostgreSQL and have < ~10M chunks | pgvector |
| Need hybrid keyword + semantic search at scale | Elasticsearch / OpenSearch |
| Need very low latency and already run Redis | Redis |
| Want a fully managed vector service | Pinecone, Qdrant Cloud, Atlas, S3 Vectors |
| Are writing a unit test | `SimpleVectorStore` |

## 11.8 Programmatic configuration

```java
@Bean
VectorStore productVectorStore(JdbcTemplate jdbc, EmbeddingModel embeddingModel) {
    return PgVectorStore.builder(jdbc, embeddingModel)
            .vectorTableName("product_vectors")
            .dimensions(1536)
            .distanceType(PgVectorStore.PgDistanceType.COSINE_DISTANCE)
            .indexType(PgVectorStore.PgIndexType.HNSW)
            .initializeSchema(false)
            .build();
}
```

Multiple stores (e.g. `policy_vectors` and `product_vectors`) are just multiple beans with qualifiers.

## 11.9 Performance tuning

- **Index**: HNSW gives good recall/latency; build it after bulk loads for speed.
- **topK**: 3–8 for RAG; more context rarely helps and costs tokens.
- **Filter selectivity**: highly selective filters with HNSW can reduce recall; test with real filters.
- Index metadata fields you filter on (Postgres: expression indexes on `metadata->>'tenant'`).
- Monitor `db.vector.client.operation` latency ([Observability](17-observability.md)).

## Common mistakes

| Mistake | Fix |
|---|---|
| `initialize-schema: true` in prod | Flyway migrations |
| Dimensions mismatch | Match `dimensions` to the embedding model |
| No tenant filter | Mandatory server-side filter wrapper |
| Random ids → duplicates on re-ingest | Deterministic UUIDs from source + chunk index |
| Threshold left at 0.0 | Calibrate a threshold, or rely on topK + evaluation |

## Checkpoint

- [ ] pgvector table created by Flyway with the right dimensions
- [ ] A search with a tenant filter returns scored documents
- [ ] Re-ingesting a document doesn't create duplicates

Next: [12 · ETL: Ingesting Documents](12-etl-pipeline.md)
