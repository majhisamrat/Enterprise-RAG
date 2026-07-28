export interface BlogPost {
  id: string;
  title: string;
  summary: string;
  content: string;
  category: string;
  author: string;
  date: string;
  readTime: number;
  featured: boolean;
  image?: string;
  tags: string[];
}

export const blogPosts: BlogPost[] = [
  {
    id: 'getting-started-rag',
    title: 'Getting Started with Enterprise RAG: A Beginner\'s Guide',
    summary: 'Learn the fundamentals of Retrieval-Augmented Generation for enterprise applications. Understand how RAG combines document retrieval with AI to deliver accurate, contextual answers.',
    content: `
## What is Enterprise RAG?

Retrieval-Augmented Generation (RAG) is an AI architecture that combines:

1. **Document Retrieval**: Finding the most relevant documents from your knowledge base
2. **Context Enhancement**: Feeding retrieved content to an LLM as context
3. **Generation**: Producing accurate answers based on your specific data

Unlike generic LLMs trained on internet data, Enterprise RAG uses YOUR company documents to provide precise, proprietary answers.

## Key Components

### Document Ingestion Pipeline
- Parse multiple formats (PDF, Word, Markdown, HTML)
- Extract and clean text content
- Remove headers, footers, and noise
- Preserve document structure and metadata

### Embedding & Indexing
- Convert text chunks into vector embeddings
- Store in vector database (Qdrant, Pinecone, etc.)
- Create searchable index for fast retrieval

### Retrieval Engine
- Accept user queries
- Convert queries to embeddings
- Search vector database for similar content
- Return top-K most relevant documents

### Generation Pipeline
- Combine query + retrieved documents
- Send to LLM with system prompts
- Generate contextual, accurate responses

## Real-World Example

**Query**: "What's our policy on remote work approval?"

**Traditional LLM**: Returns generic info or makes up policies
**Enterprise RAG**: 
1. Searches your policy documents
2. Retrieves official remote work policy
3. LLM generates response based on YOUR actual policy
4. Cites exact policy sections

## Why Enterprise RAG Matters

- **Accuracy**: Answers backed by your actual documents
- **Security**: Data stays within your infrastructure
- **Control**: You decide what information is available
- **Cost**: Reduce manual support ticket resolution time
- **Compliance**: Audit trail of which documents were used

## Getting Started

1. **Collect Documents**: Gather all relevant knowledge documents
2. **Set Up Infrastructure**: Deploy vector DB and embedding models
3. **Ingest Content**: Process documents through the pipeline
4. **Test Retrieval**: Validate that queries find relevant documents
5. **Fine-tune**: Adjust chunking, embeddings, and ranking

## Next Steps

Explore our platform to ingest your first document and run test queries. Start with a small pilot using internal documentation, then expand to customer-facing knowledge bases.
    `,
    category: 'Getting Started',
    author: 'Enterprise RAG Team',
    date: '2024-07-28',
    readTime: 7,
    featured: true,
    tags: ['RAG', 'Beginner', 'Introduction', 'Fundamentals'],
  },
  {
    id: 'building-knowledge-base',
    title: 'Building Your First Knowledge Base: Step-by-Step Tutorial',
    summary: 'A practical walkthrough of creating, uploading, and testing your first knowledge base using Enterprise RAG. Learn best practices for document organization and optimization.',
    content: `
## Phase 1: Planning Your Knowledge Base

Before uploading documents, think strategically:

### What Documents to Include
- Customer FAQs and help articles
- Internal policies and procedures
- Product documentation
- Training materials
- API references
- Troubleshooting guides

### What to Exclude
- Sensitive personal information
- Outdated/deprecated documentation
- Marketing materials (unless relevant)
- Duplicate content across sources

### Organization Strategy
Create logical categories:
- **Product Docs** (subdivided by product)
- **Sales & Customer** (pricing, contracts, case studies)
- **Operations** (HR policies, security, compliance)
- **Technical** (architecture, API, deployment)

## Phase 2: Document Preparation

### Document Quality Checklist
- [ ] UTF-8 encoding (no encoding issues)
- [ ] Clear section headers and hierarchy
- [ ] Consistent formatting
- [ ] Remove scanned images (use OCR first)
- [ ] Extract tables into structured format
- [ ] Add metadata (source, date, owner)

### Supported Formats
- PDF (text and scanned with OCR)
- Word (.docx)
- Markdown (.md)
- HTML files
- Plain text

### Document Size Guidelines
- Individual docs: 1MB - 100MB
- Total knowledge base: Start with 100MB, scale to GB
- Chunk size: 512-1024 tokens (typically 300-800 words)

## Phase 3: Upload & Ingestion

### Step 1: Create Collection
\`\`\`
1. Click "New Collection" in Dashboard
2. Name: "Company Knowledge Base"
3. Choose embedding model: BAAI/bge-base-en (recommended)
4. Set chunk size: 512 tokens
5. Set overlap: 128 tokens
\`\`\`

### Step 2: Upload Documents
\`\`\`
1. Click "Upload Documents"
2. Select multiple files (drag & drop supported)
3. Set category/tags for each document
4. Click "Process"
\`\`\`

### Step 3: Monitor Processing
- Watch progress indicator
- Check for errors (encoding issues, parsing problems)
- Typical processing: ~1MB per 2-3 seconds
- Embeddings generated automatically

## Phase 4: Testing & Validation

### Test Queries
Start with queries you know the answers to:

**Good test questions**:
- "What is our remote work policy?"
- "How do I reset my password?"
- "What are the API rate limits?"

**Check results**:
- Are top-5 results relevant?
- Do they contain accurate information?
- Are sources properly cited?

### Quality Metrics
- **Retrieval Accuracy**: % of relevant results in top-5
- **Source Diversity**: Do results come from multiple documents?
- **Citation Quality**: Can users verify sources?

### Optimization Tips
If results aren't great:
1. **Adjust Chunk Size**: Larger chunks for narrative docs, smaller for specs
2. **Add Metadata**: Tag documents by topic for better filtering
3. **Improve Queries**: Use specific, document-informed terminology
4. **Refine Documents**: Fix formatting issues, combine related docs

## Phase 5: Production Deployment

### Before Going Live
- [ ] Test 50+ real user queries
- [ ] Verify retrieval accuracy > 80%
- [ ] Set up monitoring and alerts
- [ ] Train support team on system
- [ ] Plan for regular updates

### Ongoing Maintenance
- Monthly: Review failed queries
- Quarterly: Update documents and re-index
- Continuously: Add new documents as they're created

## Common Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Slow retrieval | Increase chunk overlap, optimize embedding model |
| Irrelevant results | Restructure documents, add more context |
| Missing key info | Audit knowledge base gaps, add documents |
| Duplicates | Deduplicate during processing, use unique identifiers |

## Performance Benchmarks

With proper setup, expect:
- Query latency: 100-500ms
- Retrieval accuracy: 85-95%
- Cost per query: $0.001-$0.01
- Index size: 10-50% of original document size

Start small, validate results, then scale confidently!
    `,
    category: 'Tutorial',
    author: 'Product Team',
    date: '2024-07-25',
    readTime: 12,
    featured: true,
    tags: ['Knowledge Base', 'Tutorial', 'Setup', 'Best Practices'],
  },
  {
    id: 'production-optimization',
    title: 'Optimizing Retrieval Accuracy in Production: Metrics & Tuning',
    summary: 'Master the metrics that matter and learn advanced tuning techniques to maximize retrieval accuracy, reduce latency, and improve user satisfaction.',
    content: `
## Key Performance Metrics

### 1. Retrieval Accuracy Metrics

**Mean Reciprocal Rank (MRR)**
- Measures ranking quality of results
- Formula: 1/rank_of_first_relevant_result
- Target: > 0.8 (relevant result in top-3)

**Normalized Discounted Cumulative Gain (NDCG)**
- Combines relevance and ranking position
- Accounts for graded relevance (some results "more relevant")
- Target: > 0.85 for top-5 results

**Recall@K**
- Percentage of relevant documents retrieved in top-K
- Recall@5: Do we find the right doc in top-5?
- Recall@10: Do we find it in top-10?
- Target: > 90% Recall@10

### 2. Latency Metrics

Track these percentiles:
- **p50 (median)**: Typical query time
- **p95**: 95% of queries faster than this
- **p99**: Maximum expected latency
- **Target**: p99 < 1 second

### 3. Business Metrics

- **Query Success Rate**: % queries with relevant results
- **User Click-Through Rate**: % users find results helpful
- **Support Ticket Reduction**: Queries answered without human intervention
- **Cost per Query**: API costs + compute costs

## Tuning Framework

### Chunk Size Optimization

**Too Small Chunks (< 256 tokens)**
- ❌ Lost context, fragments concepts
- ✅ Faster search, lower latency

**Optimal Range (512-1024 tokens)**
- ✅ Preserves semantic units
- ✅ Balanced retrieval quality
- ✅ Reasonable latency

**Too Large Chunks (> 2048 tokens)**
- ❌ Slower search, higher latency
- ❌ Noise in results
- ✅ Full context preservation

**Recommendation**: Start with 512, test 256-1024, measure MRR/NDCG

### Overlap Strategy

Overlap prevents losing information at chunk boundaries.

**Rule of thumb**: Overlap = Chunk Size / 4
- 512 tokens → 128 token overlap
- 1024 tokens → 256 token overlap

Test overlap impact:
- 0% overlap: Fast but misses context
- 25% overlap: Balanced (recommended)
- 50% overlap: Highest quality but slower

### Embedding Model Selection

**Lightweight Models** (BAAI/bge-small-en)
- Speed: 10x faster
- Quality: 5-10% lower accuracy
- Cost: 50% less
- Use for: Quick prototypes, real-time searches

**Standard Models** (BAAI/bge-base-en, all-MiniLM-L6-v2)
- Speed: Balanced
- Quality: Good (90%+ accuracy)
- Cost: Reasonable
- Use for: Production systems (RECOMMENDED)

**Large Models** (BAAI/bge-large-en)
- Speed: Slower
- Quality: 95%+ accuracy
- Cost: Higher
- Use for: High-stakes domains (legal, medical)

### Hybrid Search Tuning

For enterprises, combine:
- **Dense Search**: Semantic similarity (80% weight)
- **Sparse Search**: BM25 keyword matching (20% weight)

**Weight tuning**:
- More structured data → Increase BM25 weight
- More narrative content → Decrease BM25 weight

Example query performance:
\`\`\`
Query: "API rate limits v2 integration"
Vector only: ~60% precision
BM25 only: ~50% precision
Hybrid (0.8v + 0.2s): ~95% precision
\`\`\`

## Advanced Techniques

### 1. Re-ranking with Cross-Encoders

After retrieval, re-rank results with higher accuracy:

\`\`\`python
# Initial retrieval: 100 candidates
candidates = vector_db.search(query, top_k=100)

# Re-rank top-20
reranked = cross_encoder.rank(
    pairs=[(query, doc) for doc in candidates[:20]],
    top_k=5
)
\`\`\`

Benefit: 15-20% accuracy improvement with minimal latency cost

### 2. Query Expansion

Augment user query with related terms:

**Original**: "password reset"
**Expanded**: "password reset, account recovery, login issues, authentication problems"

Increases coverage from ~75% to ~90% of relevant documents

### 3. Semantic Caching

Cache embeddings for common queries:

\`\`\`python
cache = {
    "What is RAG?": [doc1, doc2, doc3],
    "How to deploy?": [doc4, doc5, doc6],
}

# Check cache first
if query in cache:
    return cache[query]  # instant response
\`\`\`

Reduces latency for 20-30% of queries to < 50ms

## Monitoring in Production

### Set Up Dashboards

Track daily:
- Average query latency
- p99 latency
- Retrieval accuracy (sample 10% of queries)
- Failed query count
- Cost per query

### Alert Thresholds

Alert when:
- p99 latency > 1.5s (degradation)
- Retrieval accuracy < 80% (quality drop)
- Error rate > 1% (system issues)
- Cost/query > $0.01 (budget alert)

### Weekly Review

- Analyze failed queries
- Identify new synonyms/terminology
- Adjust chunk/overlap sizes if needed
- Update embeddings for changed content

## Case Study: Enterprise SaaS

**Before Optimization**:
- Accuracy: 72%
- p99 latency: 2.3s
- User satisfaction: 65%

**Optimizations Applied**:
- Chunk size: 256 → 512 tokens
- Added hybrid search (20% BM25)
- Cross-encoder re-ranking
- Query caching

**After Optimization**:
- Accuracy: 91% (+26%)
- p99 latency: 450ms (-80%)
- User satisfaction: 89% (+37%)
- Cost: $0.008/query (+0.3%)

## Conclusion

Retrieval accuracy isn't one-off tuning—it's continuous optimization. Monitor your metrics weekly, adjust parameters monthly, and aim for constant improvement in both accuracy and user satisfaction.
    `,
    category: 'Optimization',
    author: 'Engineering Team',
    date: '2024-07-20',
    readTime: 15,
    featured: true,
    tags: ['Performance', 'Metrics', 'Tuning', 'Production'],
  },
  {
    id: 'multi-tenant-rag',
    title: 'Multi-Tenant RAG: Isolating Data & Scaling Across Organizations',
    summary: 'Advanced architecture patterns for building RAG systems that securely serve multiple enterprise customers with complete data isolation and organization-level access control.',
    content: `
## Multi-Tenancy Fundamentals

Multi-tenant RAG systems serve multiple organizations with:
- **Complete data isolation**: Customer A never sees Customer B data
- **Shared infrastructure**: Cost-efficient resource utilization
- **Organization-level access**: Role-based permissions per org
- **Scalable performance**: Automatic resource allocation

## Architecture Patterns

### Pattern 1: Separate Vector Databases per Tenant
\`\`\`
Organization 1 → Qdrant Cluster 1
Organization 2 → Qdrant Cluster 2
Organization 3 → Qdrant Cluster 3
\`\`\`

**Pros**:
- ✅ Complete data isolation
- ✅ Independent scaling per org
- ✅ Audit trail per org

**Cons**:
- ❌ Higher infrastructure cost
- ❌ Complex cluster management
- ❌ Resource waste for small orgs

**Best for**: Large enterprises, compliance-heavy industries

### Pattern 2: Shared Database with Namespace Partitioning
\`\`\`
Single Qdrant Cluster
├── Collection: org-1-documents
├── Collection: org-2-documents
└── Collection: org-3-documents
\`\`\`

**Pros**:
- ✅ Cost-efficient
- ✅ Simpler infrastructure
- ✅ Easy to scale new orgs

**Cons**:
- ❌ Shared resource contention
- ❌ Risk of cross-org data leakage
- ❌ Single point of failure

**Best for**: SMBs, SaaS platforms, startups

### Pattern 3: Shared Database with Row-Level Security (Recommended)
\`\`\`
Single Qdrant Collection
├── All documents with metadata: org_id=1
├── All documents with metadata: org_id=2
└── All documents with metadata: org_id=3

Query filter: where org_id = current_user_org
\`\`\`

**Pros**:
- ✅ Maximum cost efficiency
- ✅ Simple to manage
- ✅ Good for 10-1000 orgs
- ✅ Query-level access control

**Cons**:
- ⚠️ Requires careful query design
- ⚠️ Potential for filter bypass
- ⚠️ Shared performance impact

**Best for**: Most SaaS applications

## Implementation: Pattern 3 (Recommended)

### Database Schema

\`\`\`python
class Document(Base):
    __tablename__ = "documents"
    
    id: str
    organization_id: str  # ← Critical for isolation
    content: str
    embedding: Vector  # Stored in Qdrant
    source: str
    uploaded_at: datetime
    owner_user_id: str
    
    # Metadata for retrieval
    category: str
    tags: List[str]
    is_private: bool  # Private within org only
\`\`\`

### Query with Org Isolation

\`\`\`python
async def search(
    query: str,
    user: User,  # Contains org_id
    top_k: int = 5
):
    # Build org filter
    org_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="organization_id",
                match=models.MatchValue(value=user.org_id)
            )
        ]
    )
    
    # Search only this org's documents
    results = qdrant_client.search(
        collection_name="all_documents",
        query_vector=embedding_model.encode(query),
        query_filter=org_filter,
        limit=top_k
    )
    
    return results
\`\`\`

### Authentication Enforcement

Every query MUST verify organization:

\`\`\`python
@app.post("/search")
async def search_endpoint(
    query: str,
    token: str = Header()
):
    # Verify token
    user = verify_google_token(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    
    # Verify user belongs to org
    org = db.organizations.find_one({"id": user.org_id})
    if not org:
        raise HTTPException(403, "Org not found")
    
    # Check user is member of org
    member = db.org_members.find_one({
        "org_id": user.org_id,
        "user_id": user.id
    })
    if not member:
        raise HTTPException(403, "Not org member")
    
    # Proceed with search (org_id already verified)
    return await search(query, user)
\`\`\`

## Scaling Considerations

### Embeddings Cache per Org

Cache popular query embeddings:

\`\`\`python
cache = LRUCache(max_size=10000)

def get_embedding(query: str, org_id: str):
    key = f"{org_id}:{query}"
    
    if key in cache:
        return cache[key]  # Cache hit: 1ms
    
    # Cache miss: compute & store
    embedding = model.encode(query)
    cache[key] = embedding
    return embedding
\`\`\`

### Organization-Level Rate Limiting

\`\`\`python
limiter = RateLimiter(rate="100/minute")

@app.post("/search")
@limiter.limit("100/minute")
async def search_endpoint(query: str, user: User):
    # Rate limit per org
    org_limit = db.get_org_limits(user.org_id)
    if requests_this_minute[user.org_id] > org_limit:
        raise HTTPException(429, "Rate limit exceeded")
    
    return await search(query, user)
\`\`\`

### Compute Resource Allocation

Monitor org usage:

\`\`\`python
# Daily metrics per org
org_metrics = {
    "org-1": {
        "queries": 5000,
        "avg_latency": 200,
        "embeddings_cached": 850,
        "cost": $2.50
    },
    "org-2": {
        "queries": 15000,
        "avg_latency": 350,
        "embeddings_cached": 2100,
        "cost": $6.75
    }
}
\`\`\`

Scale resources if:
- Queries/minute > threshold
- p99 latency > target
- Cost per query increasing

## Security Checklist

- [ ] All queries include org_id filter
- [ ] Org_id comes from verified token (never user input)
- [ ] Audit logs track who searched for what
- [ ] Regular cross-org data leakage tests
- [ ] Embeddings don't leak org information
- [ ] API keys scoped to organization
- [ ] Rate limits enforce per-org, not per-user
- [ ] Encryption in transit (TLS) and at rest

## Production Example: 50 Organizations

**Infrastructure**:
- 1 Qdrant cluster (32GB)
- ~5M documents across all orgs
- Average org: 100K documents

**Performance**:
- Query latency: p99 < 500ms
- Accuracy: 90%+
- Throughput: 1000 queries/second
- Monthly cost: $15K (shared infrastructure)

**Per-Org Cost**: $300/month (vs $2K+ with separate DBs)

## Conclusion

Multi-tenant RAG systems with proper isolation, authentication, and access control allow you to efficiently serve many organizations while maintaining security and compliance. Start with Pattern 3 (shared DB, row-level filtering) and evolve to Pattern 1 (separate DBs) only if specific orgs require complete isolation.
    `,
    category: 'Advanced',
    author: 'Platform Team',
    date: '2024-07-15',
    readTime: 14,
    featured: true,
    tags: ['Multi-Tenant', 'Security', 'Architecture', 'Scaling'],
  },
  {
    id: 'hybrid-rag',
    title: 'Why Hybrid Vector & Sparse Search Wins in Enterprise RAG',
    summary: 'Dense embeddings excel at conceptual semantic match, but miss exact IDs and technical codes. Discover how BM25 + Vector fusion delivers 98%+ retrieval accuracy.',
    content: `
## Understanding the Challenge

Enterprise RAG systems face a fundamental problem: balancing semantic understanding with exact matching. Traditional vector-only approaches often fail when:

- Searching for technical identifiers (API keys, ticket numbers)
- Finding exact product codes or part numbers
- Locating specific formatted data structures

## The Solution: Hybrid Search

By combining dense embeddings with sparse keyword matching, we achieve:

- **98%+ Retrieval Accuracy**: Better precision than vector-only solutions
- **Instant Exact Matches**: BM25 catches what vectors miss
- **Semantic Understanding**: Vectors understand context and meaning
- **Sub-100ms Latency**: Parallel query execution across both engines

## Implementation Details

Our implementation uses Qdrant for dense vectors and integrates BM25 sparse search, allowing queries to be scored across both dimensions and combined intelligently.

### Example Query Performance
- "Authentication failure in module_v2.py" 
- Vector-only: Would find general auth docs (~60% precision)
- Hybrid: Finds exact file + general auth context (~98% precision)

## Benchmarks

Testing across 50,000+ enterprise documents shows consistent improvements in both precision and recall when using the hybrid approach.
    `,
    category: 'Architecture',
    author: 'Enterprise RAG Team',
    date: '2024-01-15',
    readTime: 5,
    featured: false,
    tags: ['RAG', 'Vector Search', 'BM25', 'Architecture'],
  },
  {
    id: 'embeddings-performance',
    title: 'Pre-Warming BAAI Embeddings & Cross-Encoders on FastAPI',
    summary: 'How pre-loading heavy SentenceTransformer models during FastAPI startup lifecycle eliminates cold-start latencies for real-time document search.',
    content: `
## The Cold Start Problem

When deploying embedding models, the first request can take 30-60 seconds:
- Model loading from disk
- CUDA initialization
- Warmup predictions

## Solution: Lifespan Context Manager

FastAPI provides lifespan context managers that run during server startup:

\`\`\`python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models on startup
    app.state.embedder = SentenceTransformer('BAAI/bge-base-en')
    app.state.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    yield
    # Cleanup on shutdown

app = FastAPI(lifespan=lifespan)
\`\`\`

## Performance Gains

- **Cold Start**: 30-60s → 0s
- **First Query**: 2-3s → 100-150ms
- **Throughput**: 10 queries/sec → 100+ queries/sec

## Monitoring Tips

Track these metrics in production:
- Model loading time
- CUDA memory usage
- Query latency percentiles
    `,
    category: 'Performance',
    author: 'Engineering Team',
    date: '2024-01-10',
    readTime: 7,
    featured: false,
    tags: ['FastAPI', 'ML Models', 'Performance', 'Python'],
  },
  {
    id: 'oauth-security',
    title: 'Google OAuth 2.0 Token Verification & Org Isolation',
    summary: 'A comprehensive security breakdown of verifying Google ID tokens on the backend, managing JWT sessions, and enforcing enterprise org boundaries.',
    content: `
## OAuth 2.0 Token Verification

Google OAuth provides ID tokens that cryptographically prove user identity. The verification process:

1. **Fetch Google Public Keys**
   - Google publishes JWKS endpoint with rotation keys
   - Cache locally with TTL to reduce API calls

2. **Verify Signature**
   - Decode JWT header to get key ID
   - Look up corresponding public key
   - Verify signature using RS256 algorithm

3. **Validate Claims**
   - Check expiration time (exp)
   - Verify issued-at time (iat)
   - Confirm audience matches your app

## Organization Isolation

Multi-tenant systems need organization boundaries:

\`\`\`python
def get_org_from_token(token: str) -> str:
    claims = verify_google_token(token)
    email = claims['email']
    org = email.split('@')[1]  # domain-based
    
    # Verify org is registered
    org_doc = db.organizations.find_one({'domain': org})
    if not org_doc:
        raise UnauthorizedError("Org not registered")
    
    return org_doc['id']
\`\`\`

## Security Best Practices

- Always verify on backend (never trust frontend tokens)
- Use HTTPS for all token transmission
- Implement token rotation for long sessions
- Monitor for token reuse attacks
- Set appropriate token expiration (15-30 minutes)
    `,
    category: 'Security',
    author: 'Security Team',
    date: '2024-01-05',
    readTime: 4,
    featured: false,
    tags: ['OAuth', 'Security', 'Authentication', 'JWT'],
  },
  {
    id: 'document-chunking',
    title: 'Document Chunking Strategies for Better Retrieval',
    summary: 'Explore different chunking techniques to maximize retrieval performance while maintaining context and reducing token waste.',
    content: `
## Chunking Fundamentals

Effective chunking balances:
- **Context Window**: Too small loses context, too large wastes tokens
- **Overlap**: Prevents losing information at boundaries
- **Semantic Coherence**: Chunks should be meaningful units

## Strategies

### 1. Fixed Size Chunking
- 512 tokens with 128 overlap
- Fast and predictable
- May break semantic boundaries

### 2. Semantic Chunking
- Uses embeddings to find natural breaks
- Better context preservation
- Higher computational cost

### 3. Hierarchical Chunking
- Multiple chunk sizes (summary → detail)
- Improves retrieval across abstraction levels
- More complex implementation

## Performance Tuning

Test these metrics:
- Mean Reciprocal Rank (MRR) of top-5 results
- Actual vs predicted relevance
- End-to-end latency per query

## Recommended Settings

For most enterprise documents:
- Chunk size: 512-1024 tokens
- Overlap: 128-256 tokens
- Strategy: Semantic with hierarchical fallback
    `,
    category: 'Architecture',
    author: 'Data Team',
    date: '2024-01-01',
    readTime: 6,
    featured: false,
    tags: ['Chunking', 'Tokenization', 'Retrieval'],
  },
  {
    id: 'deployment-guide',
    title: 'Production Deployment Checklist for RAG Systems',
    summary: 'Complete guide to deploying enterprise RAG systems with high availability, monitoring, and disaster recovery.',
    content: `
## Pre-Deployment

### Infrastructure
- [ ] Load balancer configured
- [ ] Database replication enabled
- [ ] Vector DB backups configured
- [ ] CDN for static assets

### Security
- [ ] SSL/TLS certificates
- [ ] API rate limiting
- [ ] Input validation
- [ ] CORS properly configured

### Monitoring
- [ ] Prometheus metrics configured
- [ ] Log aggregation setup
- [ ] Alert thresholds defined
- [ ] Status page ready

## Deployment Steps

1. **Blue-Green Deployment**
   - Deploy to green environment
   - Route 5% traffic for smoke testing
   - Gradually increase to 100%
   - Keep blue running for rollback

2. **Database Migrations**
   - Test against production schema
   - Plan for downtime windows
   - Have rollback scripts ready

3. **Model Updates**
   - Version all ML models
   - A/B test new embeddings
   - Monitor retrieval metrics

## Post-Deployment

- Monitor error rates (target < 0.1%)
- Track query latency (p99 < 1s)
- Verify data consistency
- Test failover scenarios

## Disaster Recovery

- Maintain encrypted backups
- Document recovery procedures
- Practice recovery drills monthly
    `,
    category: 'Operations',
    author: 'DevOps Team',
    date: '2023-12-28',
    readTime: 8,
    featured: false,
    tags: ['Deployment', 'Operations', 'DevOps'],
  },
];

export function getFeaturedPosts(): BlogPost[] {
  return blogPosts.filter(post => post.featured);
}

export function getPostsByCategory(category: string): BlogPost[] {
  return blogPosts.filter(post => post.category.toLowerCase() === category.toLowerCase());
}

export function getPostById(id: string): BlogPost | undefined {
  return blogPosts.find(post => post.id === id);
}

export function getAllCategories(): string[] {
  return Array.from(new Set(blogPosts.map(post => post.category)));
}
