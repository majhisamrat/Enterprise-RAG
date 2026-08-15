# PHASE 0 Changes Summary

## Files Modified

### 1. `app/services/ingestion_service.py`
**Change:** Add `document_name` parameter to `upsert_document_chunks()` call

**Before (line ~95):**
```python
await self.vector_store.upsert_document_chunks(
    document=embedded_doc,
    document_id=doc_id,
    organization_id=organization_id,
    department=department,
    author=author,
    tags=tags,
    upload_id=upload_id,
    knowledge_base_id=knowledge_base_id,
)
```

**After:**
```python
await self.vector_store.upsert_document_chunks(
    document=embedded_doc,
    document_id=doc_id,
    organization_id=organization_id,
    department=department,
    author=author,
    tags=tags,
    upload_id=upload_id,
    knowledge_base_id=knowledge_base_id,
    document_name=doc_title,  # FIX: Pass actual filename
)
```

**Impact:** Vectors now store correct `document_name` (filename) instead of `f"doc_{document_id}"`

---

### 2. `app/retrieval/hybrid.py`
**Changes:** 
- Add `allowed_upload_ids` parameter
- Implement two-tier KB filtering strategy (upload_id preferred, filename fallback)
- Update field lookup order to check `document_name` first

**Before (lines ~25-52):**
```python
def retrieve(
    self,
    query: str,
    limit: int = 10,
    organization_id: Optional[uuid.UUID] = None,
    knowledge_base_id: Optional[uuid.UUID] = None,
    allowed_file_names: Optional[set] = None,
    upload_id: Optional[uuid.UUID] = None,
    department: Optional[str] = None,
) -> List[Dict[str, Any]]:
```

**After:**
```python
def retrieve(
    self,
    query: str,
    limit: int = 10,
    organization_id: Optional[uuid.UUID] = None,
    knowledge_base_id: Optional[uuid.UUID] = None,
    allowed_file_names: Optional[set] = None,
    allowed_upload_ids: Optional[set] = None,  # NEW
    upload_id: Optional[uuid.UUID] = None,
    department: Optional[str] = None,
) -> List[Dict[str, Any]]:
```

**Before (lines ~62-75, KB post-filter):**
```python
if allowed_file_names is not None and allowed_file_names:
    allowed_lowers = {f.lower() for f in allowed_file_names}
    strict_fused = []
    for doc in fused_results:
        doc_title = str(doc.get("title") or doc.get("document_id") or "").lower()
        if doc_title in allowed_lowers or any(af in doc_title for af in allowed_lowers):
            strict_fused.append(doc)
    fused_results = strict_fused
```

**After (KB post-filter with two-tier strategy):**
```python
if allowed_upload_ids is not None and allowed_upload_ids:
    # PRIMARY: Filter by upload_id (unambiguous)
    strict_fused = [d for d in fused_results if d.get("upload_id") in allowed_upload_ids]
    logger.info(f"Filtered by upload_id: {len(strict_fused)} documents")
    fused_results = strict_fused
elif allowed_file_names is not None and allowed_file_names:
    # FALLBACK: Filter by document_name or filename (for legacy vectors)
    allowed_lowers = {f.lower() for f in allowed_file_names}
    strict_fused = []
    for doc in fused_results:
        # Check document_name first (new payload field), then fallback to document_id
        doc_title = str(doc.get("document_name") or doc.get("title") or doc.get("document_id") or "").lower()
        if doc_title in allowed_lowers or any(af in doc_title for af in allowed_lowers):
            strict_fused.append(doc)
    fused_results = strict_fused
```

**Before (line ~50):**
```python
fused_results = self._local_file_search_fallback(
    query=query,
    allowed_file_names=allowed_file_names,
)
```

**After:**
```python
fused_results = self._local_file_search_fallback(
    query=query,
    allowed_file_names=allowed_file_names,
    allowed_upload_ids=allowed_upload_ids,
)
```

**Before (line ~92):**
```python
def _local_file_search_fallback(
    self,
    query: str,
    allowed_file_names: Optional[set] = None,
) -> List[Dict[str, Any]]:
```

**After:**
```python
def _local_file_search_fallback(
    self,
    query: str,
    allowed_file_names: Optional[set] = None,
    allowed_upload_ids: Optional[set] = None,
) -> List[Dict[str, Any]]:
```

**Impact:** 
- Primary filter now uses unambiguous `upload_id` set membership
- Fallback filter uses improved field lookup with `document_name` checked first
- Eliminates silent filtering failures

---

### 3. `app/orchestrator/rag.py`
**Changes:** 
- Add `allowed_upload_ids` variable
- Populate it from `Upload` records' IDs
- Pass to retriever

**Before (lines ~147-161):**
```python
allowed_file_names: Optional[set] = None

if knowledge_base_id and db_session:
    # ... code ...
    kb_uploads = await upload_repo.get_by_kb(knowledge_base_id, skip=0, limit=1000)
    allowed_file_names = set()
    for u in kb_uploads:
        if u.original_filename:
            allowed_file_names.add(u.original_filename.lower())
        if u.storage_path:
            allowed_file_names.add(Path(u.storage_path).name.lower())
```

**After:**
```python
allowed_file_names: Optional[set] = None
allowed_upload_ids: Optional[set] = None

if knowledge_base_id and db_session:
    # ... code ...
    kb_uploads = await upload_repo.get_by_kb(knowledge_base_id, skip=0, limit=1000)
    allowed_file_names = set()
    allowed_upload_ids = set()
    for u in kb_uploads:
        if u.original_filename:
            allowed_file_names.add(u.original_filename.lower())
        if u.storage_path:
            allowed_file_names.add(Path(u.storage_path).name.lower())
        if u.id:
            allowed_upload_ids.add(str(u.id))  # NEW
```

**Before (lines ~164-171):**
```python
retrieved_docs = self.retriever.retrieve(
    query=rewritten_query,
    limit=top_k,
    organization_id=organization_id,
    knowledge_base_id=knowledge_base_id,
    allowed_file_names=allowed_file_names if knowledge_base_id else None,
    department=department,
)
```

**After:**
```python
retrieved_docs = self.retriever.retrieve(
    query=rewritten_query,
    limit=top_k,
    organization_id=organization_id,
    knowledge_base_id=knowledge_base_id,
    allowed_file_names=allowed_file_names if knowledge_base_id else None,
    allowed_upload_ids=allowed_upload_ids if knowledge_base_id else None,  # NEW
    department=department,
)
```

**Impact:** Unambiguous upload IDs now threaded through entire chain

---

## Files Created

### 1. `scripts/reindex_all_uploads.py` (NEW)
**Purpose:** Re-runs ingestion for all existing uploads to fix vectors with broken `document_name`

**Features:**
- Reindexes all uploads or specific KB only
- Deletes old vectors and re-ingests files
- Supports `--dry-run` mode for preview
- Supports `--limit N` for testing
- Provides progress reporting and summary

**Usage:**
```bash
# Reindex all uploads
python scripts/reindex_all_uploads.py

# Reindex specific KB
python scripts/reindex_all_uploads.py --kb-id <uuid>

# Preview without changes
python scripts/reindex_all_uploads.py --dry-run

# Test with 5 uploads
python scripts/reindex_all_uploads.py --limit 5
```

---

### 2. `tests/test_phase0_retrieval_bug_fix.py` (NEW)
**Purpose:** Regression tests to verify PHASE 0 fixes work correctly

**Tests:**
1. **Test 1: document_name Fix**
   - Ingests a CSV file
   - Verifies vector payloads contain correct filename
   - Ensures not the broken `f"doc_{uuid}"` format

2. **Test 2: KB Isolation Verification**
   - Creates two KBs with different content
   - KB1 with "Laptop" data, KB2 with "Mouse" data
   - Verifies KB1 only retrieves Laptop content
   - Verifies KB2 only retrieves Mouse content
   - Confirms perfect isolation

**Run tests:**
```bash
pytest tests/test_phase0_retrieval_bug_fix.py -v
```

---

## Documentation Created

### 1. `PHASE0_FIXES.md`
Comprehensive documentation of:
- Problem statement and root causes
- Detailed fixes for both bugs
- Testing strategy
- Deployment checklist
- Acceptance criteria
- Performance impact
- Backward compatibility notes

### 2. `PHASE0_CHANGES_SUMMARY.md` (This file)
Quick reference of all changes, before/after code, file-by-file breakdown

---

## Summary of Changes

| Component | Change Type | Impact |
|-----------|------------|--------|
| Ingestion | Parameter added | Fixes root cause of bug 1 |
| Retrieval | Parameter added + filtering logic improved | Fixes root cause of bug 2 |
| Orchestrator | Variable added | Threads fix through system |
| Reindex Script | NEW | Fixes existing vectors |
| Regression Tests | NEW | Validates fixes |

## Verification Steps

1. **Deploy changes** to ingestion_service.py, hybrid.py, rag.py
2. **Run regression tests:**
   ```bash
   pytest tests/test_phase0_retrieval_bug_fix.py -v
   ```
3. **Execute reindex script** to fix existing vectors:
   ```bash
   python scripts/reindex_all_uploads.py
   ```
4. **Re-run tests** to confirm KB isolation works
5. **Monitor production** retrieval queries

## Rollback Plan

If issues occur:
1. Revert the three modified Python files to previous versions
2. Existing vectors won't self-heal (will need reindex after re-deploying fix)
3. KB filtering will revert to previous (broken) behavior

## Risk Assessment

**Low Risk Changes:**
- Adding `document_name` parameter (optional parameter, new vectors use it)
- Adding `allowed_upload_ids` parameter (optional, new code path, old fallback remains)
- Adding `str(u.id)` collection (new code, no impact if not passed)

**Medium Risk:**
- Reindex script deletes vectors and re-ingests (should be tested on staging first)

**Mitigation:**
- Regression tests ensure KB isolation works
- Fallback to filename filtering if upload_id unavailable
- Dry-run mode on reindex script for preview
- Can be deployed incrementally (fix ingestion first, filtering second)

---

## Next Steps

After PHASE 0 deployment and verification:

1. Run full regression suite: `pytest tests/ -v`
2. Confirm no regressions in existing PDF/DOCX/PPTX retrieval
3. Proceed to **PHASE 1**: Schema Discovery for CSV/XLSX
