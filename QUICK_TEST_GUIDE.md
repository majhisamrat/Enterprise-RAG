# Quick Test Guide - PDF Semantic Queries

## Test Environment
- **Backend**: http://localhost:8000
- **KB**: "july sales" (6686257f-beb7-4eb2-b562-6f1f80db8399)
- **PDFs**: weekly_sales_report.pdf, daily_sales_report.pdf

## Test Queries

### Test 1: Day-Based Query ✓ (Wednesday)
```
Query: "wednesday data?"
Expected: "Wednesday sales show 35 products sold, ₹35,990 revenue."
From: weekly_sales_report.pdf table (WED row)
```

### Test 2: Day-Based Query ✓ (Monday) 
```
Query: "monday sales data?"
Expected: Monday's sales figures extracted from table
From: weekly_sales_report.pdf table (MON row)
```

### Test 3: Sales Day Analysis
```
Query: "which day had best sales?"
Expected: "August 6 had the best sales with ₹58,904.45"
From: daily_sales_report.pdf or CSV data
```

### Test 4: Product Count
```
Query: "total products wednesday?"
Expected: Extract Wednesday product count from table
From: weekly_sales_report.pdf
```

### Test 5: Revenue Query
```
Query: "wednesday revenue?"
Expected: "₹35,990" 
From: weekly_sales_report.pdf table
```

## Success Criteria

### ✅ Query Works If:
1. Response contains relevant data from PDF
2. Response is 2-4 lines with explanation
3. Source shows "weekly_sales_report.pdf" or filename
4. No "No relevant documents" message

### ❌ Query Fails If:
1. Response says "No relevant documents found"
2. Response uses generic LLM knowledge (not from PDF)
3. No sources shown in response

## Checking Logs

### Sign of Fix #3 Working (404 Recovery)
```
Backend logs should show:
"Collection 'enterprise_documents_kb_6686257f' not found (404)"
"Recovery: Recreating collection 'enterprise_documents_kb_6686257f'"
"Qdrant query_points succeeded"
```

### Sign of Fix #4 Working (Fallback Filter)
```
Backend logs should show:
"Filtered by upload_id: 1 documents" (NOT 0)
"Hybrid retrieval and reranking produced 1 final context documents"
```

### Expected Full Log Sequence
```
1. Query Rewriting: original='wednesday data ?' | ...
2. Routing to SEMANTIC engine (confidence: 0.XX)
3. Running hybrid retrieval for query: 'wednesday data ?'
4. Running dense vector retrieval with KB filtering
5. [Optional] Qdrant query_points failed ... 404
6. [Optional] Recovery: Recreating collection
7. Dense Results: 0 | Sparse Results: 0
8. Vector & BM25 stores offline/empty — running fallback
9. Parsing document: weekly_sales_report.pdf
10. PDF parsed successfully (2 pages)
11. Filtered by upload_id: 1 documents ← FIX #4 WORKING
12. Hybrid retrieval produced 1 final context documents
13. [LLM Generation...]
14. RAG chat workflow completed
```

## Manual Testing Without Frontend

### Using curl:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "wednesday data?",
    "kb_id": "6686257f-beb7-4eb2-b562-6f1f80db8399"
  }'
```

### Expected Response:
```json
{
  "message": "Wednesday sales data shows 35 products sold with total revenue of ₹35,990. This data is extracted from the weekly sales report.",
  "sources": [
    {
      "file_name": "weekly_sales_report.pdf",
      "page": 1,
      "text": "WED | 35 | 35,990"
    }
  ]
}
```

## Troubleshooting

### If still getting "No relevant documents":
1. Check backend is running: `curl http://localhost:8000/api/v1/health`
2. Check PDFs exist: `ls data/uploads/raw_documents/*.pdf`
3. Check Elasticsearch running: `curl http://localhost:9200`
4. Check Qdrant running: `docker ps | grep qdrant`
5. Restart backend: `Stop then run start_local.ps1`

### If getting different data than expected:
1. Verify correct PDF uploaded
2. Check data in PDF matches query
3. Look at backend logs for which file was parsed

### If response is too long:
- This is expected behavior, LLM is including extra context
- Check logs show fallback working correctly
- Frontend will format to 2-4 lines

## Expected Timeline

| Stage | Time | Status |
|-------|------|--------|
| User sends query | 0ms | Start |
| Router classifies | +50ms | Routing complete |
| Dense search | +500ms | Qdrant search (or fallback recovery) |
| Sparse search | +500ms | Elasticsearch search |
| PDF fallback | +1500ms | Parse PDF, extract chunks |
| LLM generation | +2500ms | Groq API response |
| Total | ~5-6s | Response to user |

If taking longer, something is stuck - check logs for errors.

## Next Actions

- [ ] Test all 5 queries above
- [ ] Check backend logs for fixes working
- [ ] Verify response format is 2-4 lines
- [ ] Verify sources show actual filenames
- [ ] Report results to developer
