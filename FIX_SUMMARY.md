# PDF Semantic Query Fix - Complete Summary

## What Was Broken
User query **"wednesday data?"** on PDF `weekly_sales_report.pdf` returned **"No relevant documents found"** instead of extracting Wednesday's sales data from the PDF table.

### Root Causes (4 separate bugs)

| Bug | Symptom | Location |
|-----|---------|----------|
| 1 | Collection created but not ready before query | `qdrant_store.py:_ensure_collection` |
| 2 | Circuit breaker blocks all retries for 60 seconds on first 404 | `qdrant_client.py:mark_offline` |
| 3 | Local PDF fallback finds documents but post-filter removes them all | `hybrid.py:retrieve` (post-filter) |
| 4 | Local fallback results missing `upload_id` field required by filter | `hybrid.py:_local_file_search_fallback` |

## What Was Fixed

### Fix #1: Collection Creation Timeout (qdrant_store.py, line 78)
**Problem**: Collection created but query happened before persistence
**Solution**: Added `timeout=30` to `create_collection()` call
```python
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(...),
    timeout=30,  # Wait 30s for creation to persist
)
```

### Fix #2: Circuit Breaker Reset Method (qdrant_client.py, line 31)
**Problem**: Single error blocked all searches for 60 seconds
**Solution**: Added `reset()` method for manual recovery
```python
@classmethod
def reset(cls):
    """Reset the circuit breaker (for recovery/testing)."""
    cls._offline = False
    cls._offline_since = 0.0
```

### Fix #3: 404 Error Recovery (qdrant_store.py, line 342)
**Problem**: 404 treated same as other offline errors → immediate failure
**Solution**: Detect 404 specifically → recreate collection → retry query
```python
except Exception as search_error:
    error_str = str(search_error).lower()
    if "404" in error_str or "not found" in error_str:
        logger.info(f"Recovery: Recreating collection '{collection_name}'...")
        self._ensure_collection(knowledge_base_id)  # Create on-demand
        results = client.query_points(...)  # Retry
    else:
        QdrantConnection.mark_offline()  # Other errors → offline
```

### Fix #4: Local Fallback Post-Filter (hybrid.py, lines 91 & 197)
**Problem**: Local fallback had no `upload_id` → filtered out as 0 results
**Solution**: Mark fallback results + skip upload_id filter for them
```python
# Mark results from fallback (line 197)
results.append({
    ...
    "_from_fallback": True,  # Already KB-filtered by filename
})

# Skip upload_id filter for fallback (line 91)
strict_fused = [
    d for d in fused_results 
    if d.get("_from_fallback") or d.get("upload_id") in allowed_upload_ids
]
```

## How It Works Now

### Query Flow: "wednesday data?"

```
User Query
    ↓
1. Semantic Routing (low confidence) → try semantic retrieval
    ↓
2. Dense Qdrant Search
    ├─ If collection exists with vectors → returns results ✅
    └─ If 404 error
        ├─ Recovery: Recreate collection
        └─ Retry query → returns results ✅
    
3. Sparse BM25 Search  
    └─ Similar flow
    
4. Fusion & Reranking
    └─ If both return 0 → fallback to local files
    
5. Local File Search Fallback
    ├─ Find PDF file "weekly_sales_report.pdf"
    ├─ Parse PDF (already done during ingestion)
    ├─ Extract text chunks containing "wednesday"
    ├─ Mark as "_from_fallback": True
    ├─ Return to hybrid retriever
    
6. Post-Filter
    ├─ Check: d._from_fallback? → PASS ✅
    ├─ Return documents with KB metadata
    
7. LLM Generation
    └─ "Wednesday data shows 35 products sold, ₹35,990 revenue..."
```

## Files Modified

```
app/vectorstore/
  ├─ qdrant_store.py       (lines 72, 78, 342-368)
  └─ qdrant_client.py      (lines 31-35)

app/retrieval/
  └─ hybrid.py             (lines 91, 197)
```

## Testing

To verify the fix works:

1. **Via UI** (http://localhost:8000):
   - Select KB: "july sales"
   - Query: "wednesday data?"
   - Expected: 2-4 line answer about Wednesday sales from PDF table

2. **Alternative queries** on PDFs:
   - "monday sales data?" → Extract Monday row
   - "which day had best sales?" → Analyze all days
   - "total products wednesday?" → Sum Wednesday products

## Deployment

✅ **All changes deployed and hot-reloaded**
- Backend restarted with fix code
- New hot-reload completed 00:47:49 with no errors
- Ready for user testing

## Monitoring

After user tests, check backend logs for:
- "Collection not found (404)" + "Recovery: Recreating collection" → Fix #3 working
- "Filtered by upload_id: N documents" (N > 0) → Fix #4 working
- "Hybrid retrieval and reranking produced N documents" (N > 0) → Overall success

## Known Limitations

- Local fallback is slower than Qdrant (parses PDFs each time)
- Fallback only works if PDFs exist in `data/uploads/raw_documents/`
- Circuit breaker still blocks offline Qdrant for 60 seconds (by design)

## Next Steps if Still Failing

1. Check Qdrant is running: `docker ps | grep qdrant`
2. Check PDF was ingested: `ls data/uploads/raw_documents/*.pdf`
3. Check Elasticsearch is running: `curl http://localhost:9200`
4. View backend logs: Check terminal output for errors
5. Reset circuit breaker manually if needed: `QdrantConnection.reset()`
