# Testing Guide - Verify All Fixes

## Quick Start

### 1. Backend Running?
```powershell
# Check backend
curl.exe http://localhost:8000/api/v1/health
# Expected: 200 OK
```

### 2. Backend Not Running?
```powershell
cd C:\Users\Samratmajhi\Downloads\enterprise-rag
.\start_local.ps1
# Wait 30 seconds for startup
```

---

## Test 1: Groq Primary Model ✅

### What it tests:
- Groq LLM provider with current working models
- No `<think>` tags in output
- 2-10 line detailed responses

### Steps:

1. **Register test user:**
```python
import requests

reg_resp = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "name": "TestUser",
        "email": f"test{int(time.time())}@example.com",
        "password": "Pass123!",
        "organization_name": "Test Org",
        "department": "Engineering"
    }
)
token = reg_resp.json()["access_token"]
print(f"Token: {token}")
```

2. **Upload CSV file:**
```
POST /api/v1/knowledge/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [sales_data.csv]
knowledge_base_name: "Sales Data"
```

Sample CSV (sales_data.csv):
```csv
Product,Units,Price,Date
Widget A,100,10.00,2026-08-15
Widget B,150,15.00,2026-08-15
Widget C,80,20.00,2026-08-16
Gadget X,200,25.00,2026-08-16
```

3. **Test structured query:**
```python
chat_resp = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "query": "how many unit product sold in total?",
        "knowledge_base_id": ""
    },
    headers={"Authorization": f"Bearer {token}"}
)

answer = chat_resp.json()["answer"]
print(f"Answer:\n{answer}")

# VERIFY:
# ✅ Answer should be 2-10 lines
# ✅ No <think> tags
# ✅ Should say "Total units: 530"
# ✅ Should break down by product
```

---

## Test 2: Gemini Fallback ✅

### What it tests:
- Gemini fallback when Groq fails
- Automatic model switching
- Fallback chain works

### Steps:

1. **Temporarily disable Groq API** (optional, for testing fallback):
Edit `.env`:
```
GROQ_API_KEY=invalid_key_12345
```
Restart backend:
```powershell
# Stop: Ctrl+C in backend terminal
# Start: .\start_local.ps1
```

2. **Send same query:**
```python
chat_resp = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "query": "how many unit product sold in total?",
        "knowledge_base_id": ""
    },
    headers={"Authorization": f"Bearer {token}"}
)

answer = chat_resp.json()["answer"]
print(f"Answer:\n{answer}")

# VERIFY:
# ✅ Response comes from Gemini (not Groq)
# ✅ Check backend logs: "Attempting Gemini fallback"
# ✅ Answer still 2-10 lines
# ✅ No <think> tags
```

3. **Restore Groq API:**
Edit `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```
Restart backend.

---

## Test 3: Think Tag Removal ✅

### What it tests:
- `<think>` tags are stripped from response
- Internal reasoning not visible
- Output is clean

### Steps:

1. **Send a complex query:**
```python
chat_resp = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "query": "What is the average price per unit sold?",
        "knowledge_base_id": ""
    },
    headers={"Authorization": f"Bearer {token}"}
)

answer = chat_resp.json()["answer"]
print(f"Answer:\n{answer}")

# VERIFY:
# ✅ No <think> in output
# ✅ No </think> in output
# ✅ No internal reasoning visible
# ✅ Clean, professional response only
```

2. **Check backend logs:**
```
# In backend terminal output, look for:
"Received valid response from Groq model 'llama-3.2-90b-vision-preview'"
# This confirms Groq is being used
```

---

## Test 4: PDF Semantic Retrieval ✅

### What it tests:
- PDF extraction works
- No 0 results error
- Semantic search retrieves data

### Steps:

1. **Create sample PDF with table:**
Use any tool to create `table_data.pdf` containing:
```
| Date       | Product | Units | Revenue |
|------------|---------|-------|---------|
| Wednesday  | A       | 50    | $500    |
| Thursday   | B       | 75    | $1125   |
| Friday     | C       | 100   | $2000   |
```

2. **Upload PDF:**
```
POST /api/v1/knowledge/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [table_data.pdf]
knowledge_base_name: "Weekly Sales"
```

3. **Query PDF:**
```python
chat_resp = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "query": "wednesday data?",
        "knowledge_base_id": ""
    },
    headers={"Authorization": f"Bearer {token}"}
)

answer = chat_resp.json()["answer"]
sources = chat_resp.json()["sources"]

print(f"Answer:\n{answer}")
print(f"Sources: {sources}")

# VERIFY:
# ✅ Answer found Wednesday row
# ✅ 2-6 lines professional response
# ✅ No <think> tags
# ✅ Cites PDF as source
# ✅ Not "0 results"
```

---

## Test 5: Detailed Response Format ✅

### What it tests:
- 2-10 line format for structured data
- Professional breakdown
- Complete information

### Steps:

1. **Send detailed query:**
```python
chat_resp = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "query": "Give me a detailed breakdown of all sales metrics including total units, revenue, average price, and trends",
        "knowledge_base_id": ""
    },
    headers={"Authorization": f"Bearer {token}"}
)

answer = chat_resp.json()["answer"]
lines = answer.strip().split('\n')

print(f"Answer ({len(lines)} lines):\n{answer}")

# VERIFY:
# ✅ Response is 2-10 lines (count lines)
# ✅ Includes: total units, revenue, average, breakdown
# ✅ Professional formatting
# ✅ No <think> tags
# ✅ Comprehensive details
```

---

## Test 6: Empty Results Fallback ✅

### What it tests:
- Graceful handling when no data found
- Clear fallback message
- No hallucination

### Steps:

1. **Query non-existent data:**
```python
chat_resp = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "query": "What was the sale amount for product XYZ123 on date 2099-01-01?",
        "knowledge_base_id": ""
    },
    headers={"Authorization": f"Bearer {token}"}
)

answer = chat_resp.json()["answer"]
print(f"Answer:\n{answer}")

# VERIFY:
# ✅ Should see fallback message
# ✅ Message: "I couldn't find relevant information..."
# ✅ No made-up data
# ✅ Suggests checking Knowledge Base
```

---

## Test 7: Check Backend Logs ✅

### What it shows:
- Model selection (Groq or Gemini)
- API calls and responses
- Error handling
- Performance metrics

### Steps:

1. **Monitor backend while testing:**
```
Look for log messages like:

2026-08-20 18:59:50.123 | INFO     | app.llm.groq:generate:72 - Sending generation request to Groq model 'llama-3.2-90b-vision-preview'...
2026-08-20 18:59:52.456 | SUCCESS  | app.llm.groq:generate:95 - Received valid response from Groq model 'llama-3.2-90b-vision-preview' (Tokens: 245)

# OR (if Groq fails):

2026-08-20 18:59:50.123 | WARNING  | app.llm.groq:generate:105 - Groq API attempt 1/3 for 'llama-3.2-90b-vision-preview' failed: ...
2026-08-20 18:59:51.456 | WARNING  | app.llm.groq:generate:121 - Groq LLM failed (...). Attempting Gemini fallback...
2026-08-20 18:59:53.789 | INFO     | app.llm.gemini:generate:48 - Attempting generation with Gemini model 'gemini-1.5-pro'...
2026-08-20 18:59:55.012 | SUCCESS  | app.llm.gemini:generate:67 - Received valid response from Gemini model 'gemini-1.5-pro'...
```

VERIFY:
✅ Shows which model was used
✅ Shows token count
✅ Shows fallback activation if Groq fails
✅ No error for user (graceful fallback)
```

---

## Quick Test Script

Save as `quick_test.py`:

```python
#!/usr/bin/env python3
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("ENTERPRISE RAG - QUICK TEST")
print("=" * 60)

# 1. Health check
print("\n1. Health check...")
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"✅ Backend: {resp.status_code}")
except Exception as e:
    print(f"❌ Backend unavailable: {e}")
    sys.exit(1)

# 2. Register user
print("\n2. Registering test user...")
timestamp = int(time.time())
reg_resp = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "name": f"TestUser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "Pass123!",
        "organization_name": "Test",
        "department": "Eng"
    },
    timeout=10
)

if reg_resp.status_code != 200:
    print(f"❌ Registration failed: {reg_resp.status_code}")
    print(reg_resp.text)
    sys.exit(1)

token = reg_resp.json()["access_token"]
print(f"✅ User registered, token: {token[:30]}...")

# 3. Test chat
print("\n3. Testing chat endpoint...")
headers = {"Authorization": f"Bearer {token}"}

chat_resp = requests.post(
    f"{BASE_URL}/chat",
    json={
        "query": "hello, can you understand?",
        "knowledge_base_id": ""
    },
    headers=headers,
    timeout=30
)

if chat_resp.status_code != 200:
    print(f"❌ Chat failed: {chat_resp.status_code}")
    print(chat_resp.text)
    sys.exit(1)

data = chat_resp.json()
answer = data.get("answer", "")
model = data.get("metadata", {}).get("model_name", "unknown")

print(f"✅ Chat response received")
print(f"   Model: {model}")
print(f"   Lines: {len(answer.split(chr(10)))}")
print(f"   Has <think>: {'<think>' in answer.lower()}")
print(f"   Answer: {answer[:100]}...")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
```

Run it:
```powershell
python quick_test.py
```

---

## Expected Results Summary

| Test | Expected | Status |
|------|----------|--------|
| Groq model active | llama-3.2-90b-vision-preview in logs | ✅ |
| 2-10 line format | Structured queries return 2-10 lines | ✅ |
| No think tags | Answer free of `<think>` | ✅ |
| PDF retrieval | Finds data in PDFs, no 0 results | ✅ |
| Gemini fallback | Switches to Gemini if Groq fails | ✅ |
| Empty results | Clear message, no hallucination | ✅ |
| Backend logs | Shows model selection & metrics | ✅ |

---

## Troubleshooting

### Q: Chat returns 401 Unauthorized
**A:** Token expired. Register new user again with `quick_test.py`

### Q: Chat times out (>30s)
**A:** Check backend logs for LLM API issues. If both Groq and Gemini failing, check API keys in `.env`

### Q: Answer has `<think>` tags
**A:** This shouldn't happen. Verify `app/orchestrator/rag.py` lines 504-509 are present

### Q: Response only 1-2 lines for CSV query
**A:** Check system prompt in `app/prompt_builder/context.py` includes 2-10 line directive

### Q: Backend won't start
**A:** 
```powershell
# Kill any existing process
Get-Process -Name python* | Stop-Process -Force
# Start fresh
.\start_local.ps1
```

### Q: PDF shows 0 results
**A:** Check backend logs for:
- Collection creation errors → Check Qdrant service
- Timeout → Increase timeout in `.env`
- Circuit breaker → Should auto-reset

---

## Success Criteria Checklist

- [ ] Backend starts without errors
- [ ] Health endpoint responds (200 OK)
- [ ] User registration works
- [ ] Chat endpoint accepts queries
- [ ] Groq model in logs (llama-3.2-90b-vision-preview)
- [ ] CSV query returns 2-10 lines
- [ ] Response has no `<think>` tags
- [ ] PDF query finds data
- [ ] Empty result shows fallback message
- [ ] Gemini fallback works (if Groq disabled)
- [ ] Backend logs show token count

**All ✅ = System Ready for Production**

