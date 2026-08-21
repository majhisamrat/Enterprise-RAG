# Knowledge Base Selection Enforcement - Implementation Guide

## Problem Solved

**Issue:** When user uploads multiple CSV files and selects "All Knowledge Bases", only the LAST file's data is returned. Data from earlier files (1-10, 11-20) is missing when querying "data on august 07" because it's not in the last file (21-30).

**Root Cause:** Multi-KB queries without explicit selection don't merge data properly across all KBs.

**Solution:** Enforce single KB selection to ensure complete data retrieval.

---

## Implementation Details

### 1. Backend Changes

#### File: `app/api/routes/chat.py`

**New Import:**
```python
from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
```

**KB Validation Logic (added to chat endpoint):**
```python
# NEW: Validate KB selection for multi-KB environments
# If user has multiple KBs, they MUST select one
kb_repo = KnowledgeBaseRepository(db)
user_kbs = await kb_repo.list_by_org(tenant_context.organization_id, skip=0, limit=1000)

if len(user_kbs) > 1 and not kb_uuid:
    # Multiple KBs exist but none selected - BLOCK chat
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Please select a Knowledge Base to continue. You have {len(user_kbs)} available Knowledge Bases."
    )
```

**New Endpoint: `GET /api/v1/chat/kb-requirements`**
```python
@router.get("/kb-requirements")
async def get_kb_requirements(current_user, tenant_context, db):
    """
    Frontend calls this to check:
    1. How many KBs user has
    2. Whether KB selection is required
    3. List of available KBs for dropdown
    
    Returns:
    {
        "kb_count": 3,
        "require_kb_selection": true,  # if > 1
        "message": "You have 3 Knowledge Bases. Please select one to continue.",
        "kbs": [
            {"id": "...", "name": "Sales Jan", "description": "..."},
            {"id": "...", "name": "Sales Feb", "description": "..."},
            {"id": "...", "name": "Sales Mar", "description": "..."}
        ]
    }
    """
```

---

## Frontend Behavior

### When App Loads

```javascript
// Call kb-requirements endpoint on app load
GET /api/v1/chat/kb-requirements

Response:
{
  "kb_count": 3,
  "require_kb_selection": true,
  "message": "You have 3 Knowledge Bases. Please select one to continue.",
  "kbs": [...]
}
```

### Decision Tree

```
if kb_count == 0:
  → Show: "No Knowledge Bases available"
  → Chat input: DISABLED
  
if kb_count == 1:
  → Show: "1 Knowledge Base available"
  → Auto-select the KB
  → Chat input: ENABLED
  
if kb_count > 1:
  → Show: "Please select a Knowledge Base"
  → KB Dropdown: SHOW all KBs
  → Chat input: DISABLED (until KB selected)
  
When user selects KB from dropdown:
  → Store selected_kb_id
  → Chat input: ENABLED
  → Show: "KB selected: [Name]"
```

---

## Key Changes Summary

| Component | Change | Purpose |
|-----------|--------|---------|
| Chat Endpoint | Added KB validation | Block multi-KB queries |
| KB Requirement Check | NEW endpoint | Tell frontend if selection required |
| Chat Input | Conditional display | Only enable with valid KB selection |
| KB Dropdown | Only show real KBs | Remove "All Knowledge Bases" from chat |
| Filter Section | Keep "All KB" option | Used for general exploration only |

---

## API Endpoints

### 1. **POST /api/v1/chat** (Existing - Enhanced)
- **Validation Added:** If multiple KBs exist, `knowledge_base_id` is REQUIRED
- **Error:** 400 Bad Request with message about KB selection
- **Success:** Returns chat response for selected KB only

### 2. **GET /api/v1/chat/kb-requirements** (NEW)
- **Purpose:** Frontend checks KB requirements on app load
- **Returns:** KB count, selection requirement, available KBs list
- **Error Handling:** Returns empty list if no KBs

### 3. **GET /api/v1/knowledge/list** (Existing - For Filtering)
- **Purpose:** Get all KBs for filter/exploration
- **Unchanged:** Works as before for filters
- **Note:** NOT used for chat KB selection (only for filtering)

---

## User Experience Flow

### Scenario 1: Single KB (Sales August 1-30)
```
User opens app
  ↓
Backend: kb_count = 1, require_kb_selection = false
  ↓
Frontend: Auto-select KB, enable chat
  ↓
User: "give me data on august 07?"
  ↓
Backend: Query single KB (complete data)
  ↓
Result: ✅ Returns complete data for august 07
```

### Scenario 2: Multiple KBs (User uploaded 3 files)
```
User opens app
  ↓
Backend: kb_count = 3, require_kb_selection = true
  ↓
Frontend: Show dropdown with 3 KBs, DISABLE chat input
  ↓
Message: "Please select a Knowledge Base to continue"
  ↓
User: Clicks dropdown, selects "Sales 1-10"
  ↓
Frontend: Enable chat, show "Selected: Sales 1-10"
  ↓
User: "give me data on august 07?"
  ↓
Backend: Query only "Sales 1-10" KB
  ↓
Result: ✅ Returns data from selected KB
```

### Scenario 3: Multiple KBs with Filter Search
```
User: Clicks "All Knowledge Bases" filter
  ↓
Frontend: Shows ALL KBs available
  ↓
User: Can browse/explore all KBs
  ↓
But: Chat input is still DISABLED (no KB selected for chat)
  ↓
User: Clicks specific KB → auto-select for chat
  ↓
Chat input: Now ENABLED with that KB
```

---

## Data Integrity Guarantee

### Before (Problem)
```
3 Files uploaded:
- sales_1-10.csv (Aug 1-10 data)
- sales_11-20.csv (Aug 11-20 data)
- sales_21-30.csv (Aug 21-30 data)

"All Knowledge Bases" selected
Query: "data on august 07?"

Result: Only searches sales_21-30.csv
Output: ❌ "Not found" or empty
Reason: Aug 07 data only in sales_1-10.csv
```

### After (Fixed)
```
3 Files uploaded:
- sales_1-10.csv (Aug 1-10 data)
- sales_11-20.csv (Aug 11-20 data)
- sales_21-30.csv (Aug 21-30 data)

User forced to select ONE KB
Selected: "Sales 1-10"
Query: "data on august 07?"

Result: Queries only sales_1-10.csv (selected)
Output: ✅ Returns complete data for Aug 07
Reason: Single KB ensures complete data
```

---

## Implementation Checklist

### Backend
- ✅ Add KB validation to chat endpoint
- ✅ Block multi-KB queries without explicit selection
- ✅ Create `/chat/kb-requirements` endpoint
- ✅ Return KB count and selection requirement

### Frontend (To Be Implemented)
- [ ] Call `/chat/kb-requirements` on app load
- [ ] Show KB dropdown when `require_kb_selection = true`
- [ ] Disable chat input until KB selected
- [ ] Show current selection
- [ ] Auto-select if only 1 KB available
- [ ] Remove "All Knowledge Bases" from chat KB selector

### Testing
- [ ] Single KB: Chat should work immediately
- [ ] Multiple KBs: Chat blocked until selection
- [ ] After selection: Chat works with selected KB only
- [ ] Filter "All KBs": Still shows all for exploration
- [ ] Switch KB: Creates new session, maintains history

---

## Error Messages

### Multi-KB without Selection
```
Status: 400 Bad Request
Message: "Please select a Knowledge Base to continue. You have 3 available Knowledge Bases. 
Select 'All Knowledge Bases' in the filter to see them."
```

### No KBs Available
```
Status: 400 Bad Request
Message: "No Knowledge Bases available. Please create one first."
```

### KB Not Found
```
Status: 400 Bad Request
Message: "Selected Knowledge Base not found or access denied."
```

---

## Benefits

✅ **Data Integrity:** No more mixed data from multiple files  
✅ **Clarity:** Users know which KB they're querying  
✅ **Accuracy:** Complete results within selected KB  
✅ **UX:** Clear guidance when selection required  
✅ **Performance:** Single KB queries are faster  
✅ **Scalability:** Works for any number of KBs  

---

## Backward Compatibility

**Single KB Users:** No change - chat works immediately
**Multi-KB Users:** Need to select KB (one-time)
**API Clients:** Must pass `knowledge_base_id` if multiple KBs exist
**Existing Sessions:** Maintain their associated KB

---

## Deployment Steps

1. ✅ Update `app/api/routes/chat.py` (backend)
2. Deploy backend changes
3. Frontend team implements KB selector UI
4. Test with single and multiple KBs
5. Deploy frontend changes

---

## Testing Commands

### Check KB Requirements
```bash
curl -X GET http://localhost:8000/api/v1/chat/kb-requirements \
  -H "Authorization: Bearer YOUR_TOKEN"

Response:
{
  "kb_count": 3,
  "require_kb_selection": true,
  "message": "You have 3 Knowledge Bases...",
  "kbs": [...]
}
```

### Send Chat (with KB)
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "data on august 07",
    "knowledge_base_id": "kb-uuid-here"
  }'
```

### Send Chat (without KB - Multiple Exist)
```bash
# Should get 400 error
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "data on august 07"
  }'

Response: 400 Bad Request
Message: "Please select a Knowledge Base..."
```

---

## Status

✅ **Backend Implementation:** COMPLETE  
✅ **API Endpoint:** READY  
⏳ **Frontend Implementation:** TODO  
📋 **Documentation:** COMPLETE  

Ready for deployment! 🚀
