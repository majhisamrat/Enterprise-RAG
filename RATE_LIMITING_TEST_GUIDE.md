# Chat Rate Limiting - Testing Guide

## Overview
- **Limit**: 10 user messages per 24 hours
- **Enforcement**: Backend checks rate limit BEFORE processing message
- **Display**: Frontend shows "Daily Chat Limit Reached" alert with exact reset date/time
- **UX**: Input disabled when limit reached

---

## Architecture

### Backend (`app/utils/rate_limiter.py`)
- `ChatRateLimiter.check_rate_limit(user_id, db)` → `(is_allowed, message_count, reset_time)`
- Counts user messages with `sender_role="user"` in last 24 hours
- Calculates reset time as: earliest_message_time + 24 hours

### Backend Route (`app/api/routes/chat.py`)
- `/api/v1/chat` (POST) checks rate limit FIRST
- Returns HTTP 429 if limit exceeded with details:
  ```json
  {
    "error": "Rate limit exceeded",
    "message": "You have reached your limit...",
    "reset_time": "Aug 6, 2026 at 3:45 PM UTC",
    "message_count": 10,
    "max_messages": 10
  }
  ```

### Frontend (`frontend/src/pages/ChatPage.tsx`)
- Imports `RateLimitAlert` component
- Captures `rate_limit_info` from API response
- On 429 error, extracts reset time from error response
- Displays alert and disables input textarea + send button

### UI Component (`frontend/src/components/chat/RateLimitAlert.tsx`)
- Shows red alert: "Daily Chat Limit Reached"
- Displays: current count / max count
- Shows reset time with clock icon: "Aug 6, 2026 at 3:45 PM UTC"
- Professional styling with responsiveness

---

## Testing Scenarios

### Test 1: Send 10 Messages (Reach Limit)

**Steps:**
1. Start backend: `python -m uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Login to http://localhost:5173/login
4. Go to chat page
5. Send 10 test messages (e.g., "test 1", "test 2", ... "test 10")

**Expected Behavior:**
- Messages 1-10: Send successfully ✅
- Each message creates ChatMessage in DB with `sender_role="user"` and `created_at`
- Backend logs: `User {id} has {count}/10 messages used`

**Verify in Database:**
```bash
sqlite3 enterprise_rag.db
SELECT COUNT(*) FROM chat_messages WHERE sender_role='user' 
  AND session_id IN (SELECT id FROM chat_sessions WHERE user_id='YOUR_USER_ID')
  AND created_at > datetime('now', '-24 hours');
```

---

### Test 2: 11th Message Blocked (Limit Enforced)

**Steps:**
1. After sending 10 messages, try to send message #11
2. Click "Send" button

**Expected Behavior:**
- Request blocked with HTTP 429
- Error response shows reset time
- Frontend displays red alert: **"Daily Chat Limit Reached"**
- Alert shows:
  - "You have used all 10 of your 10 daily messages"
  - "Limit Reset: Aug 6, 2026 at 3:45 PM UTC" (calculated as: first message time + 24h)
- Input textarea becomes disabled
- Send button becomes disabled
- Placeholder text changes to: "Daily message limit reached. Try again after reset time."

**Verify in Console:**
- Check browser DevTools → Network tab → POST /api/v1/chat
- Response status: 429
- Check frontend console → useChat error handling

---

### Test 3: Reset Time Accuracy

**Steps:**
1. Check the first ChatMessage timestamp in DB
2. Compare with displayed reset time in alert

**Expected Behavior:**
- Reset time = First message creation time + 24 hours
- Format: "Aug 6, 2026 at 3:45 PM UTC"
- Example:
  - First message: Aug 5, 2026 at 3:45 PM UTC
  - Reset time: Aug 6, 2026 at 3:45 PM UTC ✅

**Database Query:**
```bash
SELECT 
  MIN(created_at) as first_message_time,
  datetime(MIN(created_at), '+24 hours') as reset_time
FROM chat_messages 
WHERE sender_role='user' 
  AND session_id IN (SELECT id FROM chat_sessions WHERE user_id='YOUR_USER_ID');
```

---

### Test 4: UI Disabled State

**Steps:**
1. When limit is reached, observe input area

**Expected Behavior:**
- Textarea has `disabled` attribute
- Send button has `disabled` attribute + opacity reduced
- Both have cursor-not-allowed style
- User cannot type or click send
- Placeholder shows rate limit message

**Browser Inspection:**
```javascript
// In DevTools console:
document.querySelector('textarea').disabled // Should be true
document.querySelector('button[type="submit"]').disabled // Should be true
```

---

### Test 5: Multiple Users Independent Limits

**Steps:**
1. Create two user accounts
2. User A sends 10 messages
3. Switch to User B
4. User B should be able to send messages (not blocked)

**Expected Behavior:**
- Rate limit is per-user, not global
- User A limit reached: can't send
- User B limit not reached: can send
- Each user's count tracked independently

**Database Verification:**
```bash
SELECT 
  cs.user_id,
  COUNT(cm.id) as message_count
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.id = cm.session_id 
  AND cm.sender_role='user'
  AND cm.created_at > datetime('now', '-24 hours')
GROUP BY cs.user_id;
```

---

### Test 6: Message Type Filtering

**Steps:**
1. Send 5 user messages
2. Check the count

**Expected Behavior:**
- Only messages with `sender_role='user'` are counted
- Assistant responses don't count toward limit
- System messages don't count

**Database Query:**
```bash
SELECT sender_role, COUNT(*) FROM chat_messages 
WHERE session_id IN (SELECT id FROM chat_sessions WHERE user_id='YOUR_USER_ID')
GROUP BY sender_role;
```

---

## Backend Logs to Check

When testing, look for these log messages:

```
✅ Successful messages:
[INFO] User {id} has 5/10 messages used

❌ Limit exceeded:
[WARNING] Rate limit exceeded for user {id}. Messages: 10/10. Reset: Aug 6, 2026 at 3:45 PM UTC
```

---

## Frontend Error Handling

**Test what happens if:**

1. **Network error**: Try disconnecting internet → error handled gracefully
2. **Invalid response**: Manually send bad data → component still works
3. **Empty reset_time**: Fallback should work if time calculation fails
4. **Page refresh**: Rate limit state should persist (captured from API)

---

## Debugging Checklist

- [ ] Backend rate limiter imports working
- [ ] ChatMessage table has `created_at` timestamps
- [ ] `sender_role='user'` filter working
- [ ] 24-hour window calculation correct
- [ ] Reset time = earliest_message_time + 24h
- [ ] 429 error response includes reset_time
- [ ] Frontend captures 429 error
- [ ] RateLimitAlert displays
- [ ] Input disabled when limit reached
- [ ] Reset time formats correctly (e.g., "Aug 6, 2026 at 3:45 PM UTC")

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
  COUNT(*) as total_messages,
  COUNT(CASE WHEN sender_role='user' THEN 1 END) as user_messages,
  COUNT(CASE WHEN sender_role='assistant' THEN 1 END) as assistant_messages
FROM chat_messages;
```

---

## Expected Outcomes

✅ **Passing Criteria:**
1. User can send exactly 10 messages
2. 11th message is blocked with 429 error
3. Alert displays with correct reset time (date + time)
4. Input becomes disabled when limit reached
5. Rate limit is per-user, not global
6. Reset time = first message time + 24 hours
7. Only user messages counted (not assistant)

❌ **Failing Criteria:**
- User can send more than 10 messages
- No error or alert shown
- Reset time is wrong or missing
- Input doesn't disable
- Rate limit blocks multiple users
- Assistant messages counted toward limit

---

## After Successful Testing

Run comprehensive tests to confirm everything works:
```bash
# Run backend tests (if available)
pytest tests/test_rate_limiter.py -v

# Run frontend tests (if available)
npm test -- --testPathPattern=ChatPage
```

---

## Notes

- Rate limit window: **24 hours** (rolling, not calendar day)
- Max messages: **10 per 24 hours per user**
- Reset time format: "Mon, DD YYYY at HH:MM AM/PM UTC"
- Limit checked **before** message processing
- Both user and assistant messages stored, but **only user messages counted**
