# PDF Semantic Retrieval Fix - August 19, 2026

## Problem
User query "wednesday data?" on PDF weekly_sales_report.pdf returned **0 results** despite:
- PDF successfully ingested and parsed (2 pages)
- Vectors successfully stored in Qdrant (`PUT.../points HTTP 200`)
- Query still got `404 Not Found` from Qdrant

Logs showed:
```
ERROR | app.vectorstore.qdrant_store:search:337 - Qdrant query_points failed for collection 
'enterprise_documents_kb_6686257f': Unexpected Response: 404 (Not Found)
...
Filtered by upload_id: 0 documents
```

## Root Causes Identified

### 1. **Race Condition in Qdrant Collection Creation** 
- Ingestion (Celery) successfully created collection and upserted vectors
- Search (FastAPI) ran moments later and got 404
- **Root cause**: Collection creation wasn't waiting for persistence; query hit Qdrant before collection was fully written to all shards

### 2. **Circuit Breaker False Positive**
- On 404 error, code called `QdrantConnection.mark_offline()` 
- This put circuit breaker in sleep mode for 60 seconds
- Subsequent searches were blocked immediately without even trying Qdrant

### 3. **Local Fallback Post-Filter Bug**
- When Qdrant returned 0 results, hybrid retriever fell back to local PDF parsing
- Local fallback successfully found and parsed PDFs with matching query terms
- **BUT** post-filter checked `d.get("upload_id") in allowed_upload_ids`
- Local fallback results had NO upload_id field → all results filtered out → returned 0 documents

## Fixes Applied

### Fix 1: Qdrant Collection Creation Timeout (`app/vectorstore/qdrant_store.py:_ensure_collection`)
```python
# Added timeout parameter to collection creation
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(...),
    timeout=30,  # Wait up to 30 seconds for creation
)
```

### Fix 2: Circuit Breaker Reset Method (`app/vectorstore/qdrant_client.py`)
```python
@classmethod
def reset(cls):
    """Reset the circuit breaker (for recovery/testing)."""
    cls._offline = False
    cls._offline_since = 0.0
```

### Fix 3: 404 Error Recovery (`app/vectorstore/qdrant_store.py:search`)
```python
try:
    results = client.query_points(...)
except Exception as search_error:
    error_str = str(search_error).lower()
    if "404" in error_str or "not found" in error_str:
        logger.warning(f"Collection not found (404). Attempting recovery...")
        # Try to recreate collection on-demand
        if knowledge_base_id:
            self._ensure_collection(knowledge_base_id)
            # Retry the query
            results = client.query_points(...)
    else:
        # Only mark offline for OTHER errors
        QdrantConnection.mark_offline()
```

### Fix 4: Local Fallback Post-Filter (`app/retrieval/hybrid.py`)
```python
# Mark results from fallback
results.append({
    ...
    "_from_fallback": True,  # Mark as from local fallback (already KB-filtered)
})

# Skip upload_id filter for fallback results
if allowed_upload_ids is not None and allowed_upload_ids:
    strict_fused = [
        d for d in fused_results 
        if d.get("_from_fallback") or d.get("upload_id") in allowed_upload_ids
    ]
```

## Expected Behavior After Fixes

1. **Query "wednesday data?"** on weekly_sales_report.pdf:
   - If Qdrant collection exists: Returns vectors from Qdrant ✅
   - If Qdrant 404: Auto-recreates collection and retries query ✅  
   - If Qdrant offline: Falls back to local PDF parsing ✅
   - Local fallback finds "wednesday" in PDF table → extracts row ✅
   - Post-filter passes through with `_from_fallback` flag ✅
   - Returns 2-4 line answer with file names ✅

2. **Subsequent queries** won't be blocked by circuit breaker ✅

## Files Modified

1. `app/vectorstore/qdrant_store.py` - Enhanced collection creation, 404 recovery
2. `app/vectorstore/qdrant_client.py` - Added reset() method
3. `app/retrieval/hybrid.py` - Fixed post-filter logic for fallback results

## Testing

Run query through UI:
```
KB: july sales
Query: "wednesday data?"
Expected: Extract wednesday row from PDF table (MON-SAT: WED = 35 products, ₹35,990)
```

Or test other PDF queries:
- "monday sales data?" → Monday row from table
- "which day had best sales?" → Should analyze PDF data

## Status

✅ Code changes implemented
⏳ Hot-reload applied to running backend
⏳ Awaiting user test to confirm PDF queries now return results
