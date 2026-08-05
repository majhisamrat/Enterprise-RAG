# Document Upload Rate Limiting - Testing Guide

## Overview
- **Limit**: 5 document uploads per 24 hours per user
- **Enforcement**: Backend checks limit BEFORE processing upload
- **Display**: Frontend shows "Daily Upload Limit Reached" alert with reset date/time
- **UX**: Upload button disabled when limit reached

---

## Architecture

### Backend (`app/utils/upload_limiter.py`)
- `DocumentUploadLimiter.check_upload_limit(user_id, db)` → `(is_allowed, upload_count, reset_time)`
- Counts user uploads in last 24 hours from `Upload` table
- Calculates reset time as: earliest_upload_time + 24 hours

### Backend Route (`app/api/routes/knowledge.py`)
- `POST /api/v1/knowledge/{kb_id}/upload` checks rate limit FIRST
- Returns HTTP 429 if limit exceeded with details:
  ```json
  {
    "error": "Upload limit exceeded",
    "message": "You have reached your limit of 5 documents per 24 hours.",
    "reset_time": "Aug 6, 2026 at 3:45 PM UTC",
    "upload_count": 5,
    "max_uploads": 5
  }
  ```

### Frontend (`frontend/src/pages/KnowledgeDetailPage.tsx`)
- Imports `UploadLimitAlert` component
- Captures `uploadLimitInfo` from error response (429)
- On upload failure with 429, extracts reset time from error
- Displays alert and disables "Upload Document" button

### UI Component (`frontend/src/components/knowledge/UploadLimitAlert.tsx`)
- Shows red alert: "Daily Upload Limit Reached"
- Displays: current count / max count (5)
- Shows reset time with clock icon: "Aug 6, 2026 at 3:45 PM UTC"
- Professional styling with responsiveness

---

## Testing Scenarios

### Test 1: Upload 5 Documents (Reach Limit)

**Steps:**
1. Start backend: `python -m uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Login to http://localhost:5173/login
4. Go to a knowledge base: http://localhost:5173/knowledge/{kb_id}
5. Click "Upload Document" button
6. Upload 5 test documents (PDF, DOCX, TXT, etc.)

**Expected Behavior:**
- Uploads 1-5: Upload successfully ✅
- Each upload creates `Upload` record in DB with `user_id` and `created_at`
- Backend logs: `User {id} has {count}/5 uploads used`
- Upload history shows all 5 documents

**Verify in Database:**
```bash
sqlite3 enterprise_rag.db
SELECT COUNT(*) FROM uploads WHERE user_id='YOUR_USER_ID' 
  AND created_at > datetime('now', '-24 hours');
```
Should return: 5

---

### Test 2: 6th Upload Blocked (Limit Enforced)

**Steps:**
1. After uploading 5 documents, try to upload a 6th document
2. Click "Upload Document" button
3. Select a file and click "Start Processing"

**Expected Behavior:**
- Upload request blocked with HTTP 429
- Error response shows reset time
- Upload dialog closes
- Frontend displays red alert: **"Daily Upload Limit Reached"**
- Alert shows:
  - "You have uploaded 5 of your 5 daily documents"
  - "Upload Limit Resets: Aug 6, 2026 at 3:45 PM UTC" (first upload + 24h)
- "Upload Document" button becomes disabled (grayed out)
- User cannot upload more documents

**Verify in Console:**
- Check browser DevTools → Network tab → POST /api/v1/knowledge/{kb_id}/upload
- Response status: 429
- Check frontend console for error handling

---

### Test 3: Reset Time Accuracy

**Steps:**
1. Check the first `Upload` record's `created_at` timestamp in DB
2. Compare with displayed reset time in alert

**Expected Behavior:**
- Reset time = First upload creation time + 24 hours
- Format: "MMM DD, YYYY at HH:MM AM/PM UTC"
- Example:
  - First upload: Aug 5, 2026 at 3:45 PM UTC
  - Reset time: Aug 6, 2026 at 3:45 PM UTC ✅

**Database Query:**
```bash
SELECT 
  MIN(created_at) as first_upload_time,
  datetime(MIN(created_at), '+24 hours') as reset_time
FROM uploads 
WHERE user_id='YOUR_USER_ID'
  AND created_at > datetime('now', '-24 hours');
```

---

### Test 4: Upload Button Disabled State

**Steps:**
1. When limit is reached, observe the "Upload Document" button

**Expected Behavior:**
- Button has `disabled` attribute
- Button is grayed out (opacity reduced)
- Button has `cursor-not-allowed` style
- Clicking button does nothing
- User cannot open upload dialog

**Browser Inspection:**
```javascript
// In DevTools console:
document.querySelector('button:contains("Upload Document")').disabled // Should be true
```

---

### Test 5: Alert Display in Upload History Section

**Steps:**
1. After limit is reached, scroll to "Upload History" section
2. Observe alert placement

**Expected Behavior:**
- Red alert displays at TOP of "Upload History" section
- Alert is prominent and noticeable
- Alert includes:
  - Red icon (AlertCircle)
  - Title: "Daily Upload Limit Reached"
  - Message: count / max
  - Clock icon with reset time in box
  - Small helper text: "You can upload more documents after the reset time"
- Alert persists until page refresh or new session

**UI Elements:**
- Red background: `bg-red-50/80 dark:bg-red-950/20`
- Red text: `text-red-900 dark:text-red-200`
- Clock icon: `<Clock className="h-4 w-4" />`

---

### Test 6: Multiple Users Independent Limits

**Steps:**
1. Create/login as User A
2. Upload 5 documents
3. User A limit reached: try 6th upload → blocked ✅
4. Logout and login as User B
5. User B should be able to upload (not blocked)

**Expected Behavior:**
- Upload limit is per-user, not global
- User A limit reached: can't upload
- User B limit not reached: can upload 5 documents
- Each user's count tracked independently in DB

**Database Verification:**
```bash
SELECT 
  user_id,
  COUNT(*) as upload_count
FROM uploads
WHERE created_at > datetime('now', '-24 hours')
GROUP BY user_id;
```

---

### Test 7: Upload Count by Type

**Steps:**
1. Upload different file types: PDF, DOCX, TXT, CSV
2. Check they all count toward the 5-limit

**Expected Behavior:**
- All file types count equally toward limit
- 1 PDF + 1 DOCX + 1 TXT + 1 CSV + 1 other = 5 uploads
- 6th upload of any type blocked

**Database Query:**
```bash
SELECT 
  file_type,
  COUNT(*) as count
FROM uploads 
WHERE user_id='YOUR_USER_ID'
  AND created_at > datetime('now', '-24 hours')
GROUP BY file_type;
```

---

## Backend Logs to Check

When testing, look for these log messages:

```
✅ Successful uploads:
[INFO] User {id} has 3/5 uploads used

❌ Limit exceeded:
[WARNING] Upload limit exceeded for user {id}. Uploads: 5/5. Reset: Aug 6, 2026 at 3:45 PM UTC
```

---

## Frontend Error Handling

**Test what happens if:**

1. **Network error**: Try disconnecting internet → error handled gracefully
2. **Invalid response**: Try malformed error data → fallback to generic message
3. **Empty reset_time**: If time calculation fails → "Unknown" displayed
4. **Page refresh**: Limit state persists (managed by component state)
5. **Multiple uploads queued**: Only first should fail with 429, others queued

---

## Debugging Checklist

- [ ] Backend upload limiter imports working
- [ ] `Upload` table has `created_at` timestamps
- [ ] 24-hour window calculation correct
- [ ] Reset time = earliest_upload_time + 24h
- [ ] 429 error response includes reset_time
- [ ] Frontend captures 429 error
- [ ] UploadLimitAlert displays in upload history section
- [ ] Upload button disabled when limit reached
- [ ] Reset time formats correctly (e.g., "Aug 6, 2026 at 3:45 PM UTC")
- [ ] Alert shows after upload dialog closes
- [ ] Multiple users have independent limits

---

## Quick Test Commands

**Backend:**
```bash
cd /path/to/enterprise-rag
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd /path/to/enterprise-rag/frontend
npm run dev
# Access at http://localhost:5173
```

**Database Check:**
```bash
sqlite3 enterprise_rag.db
SELECT 
  COUNT(*) as total_uploads,
  COUNT(DISTINCT user_id) as unique_users,
  COUNT(DISTINCT knowledge_base_id) as knowledge_bases
FROM uploads;
```

**Check User Upload Count:**
```bash
sqlite3 enterprise_rag.db
SELECT 
  u.original_filename,
  u.file_type,
  u.file_size_bytes,
  u.processing_status,
  u.created_at
FROM uploads u
WHERE u.user_id = 'YOUR_USER_ID'
  AND u.created_at > datetime('now', '-24 hours')
ORDER BY u.created_at DESC;
```

---

## Expected Test Results

✅ **Passing Criteria:**
1. User can upload exactly 5 documents
2. 6th upload is blocked with 429 error
3. Alert displays with correct reset time (date + time)
4. Upload button becomes disabled when limit reached
5. Alert shows in upload history section
6. Upload limit is per-user, not global
7. Reset time = first upload time + 24 hours
8. Different file types all count toward limit
9. User can upload again after reset time
10. Multiple users don't affect each other's limits

❌ **Failing Criteria:**
- User can upload more than 5 documents
- No error or alert shown
- Reset time is wrong or missing
- Upload button doesn't disable
- Alert doesn't display
- Upload limit blocks multiple users
- Reset time calculation is incorrect

---

## After Successful Testing

1. **Verify logs** show rate limit messages
2. **Check database** for correct upload timestamps
3. **Test with real files** (not just test files)
4. **Test 24-hour reset** (wait for reset or manually adjust database time)
5. **Test error recovery** (try upload after limit reached multiple times)

---

## Notes

- Upload limit window: **24 hours** (rolling, not calendar day)
- Max uploads: **5 per 24 hours per user**
- Reset time format: "Mon, DD YYYY at HH:MM AM/PM UTC"
- Limit checked **before** any file processing
- All file types count equally
- Upload button disabled when `isLimitReached` = true
- Alert displays in "Upload History" section
- Reset time calculated from earliest upload in current window

---

## Integration with Chat Limit

Both chat message limit (10/24h) and upload limit (5/24h) are now implemented:
- Chat: `/api/v1/chat` endpoint
- Upload: `/api/v1/knowledge/{kb_id}/upload` endpoint
- Both use 24-hour rolling windows
- Both show professional alerts with reset times
- Both track per-user limits independently
