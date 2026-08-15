# PHASE 0 Deployment Checklist

## Pre-Deployment Review

### Code Review
- [ ] Review `PHASE0_DIFFS.txt` for exact changes
- [ ] Review `app/services/ingestion_service.py` (1 line change)
- [ ] Review `app/retrieval/hybrid.py` (~30 lines)
- [ ] Review `app/orchestrator/rag.py` (~5 lines)
- [ ] Check backward compatibility
- [ ] Verify no SQL injection vulnerabilities
- [ ] Confirm no new dependencies added

### Documentation Review
- [ ] Read `PHASE0_EXECUTIVE_SUMMARY.txt`
- [ ] Read `PHASE0_FIXES.md` (understand root causes)
- [ ] Review `PHASE0_COMPLETE.md` (deployment guide)
- [ ] Approve all documentation

### Testing Preparation
- [ ] Review `tests/test_phase0_retrieval_bug_fix.py`
- [ ] Set up staging environment
- [ ] Prepare test data (2+ KBs with different files)
- [ ] Prepare reindex command reference

---

## Staging Deployment

### Pre-Deployment
- [ ] Take backup of current code
- [ ] Record current baseline metrics (retrieval latency, KB query times)
- [ ] Prepare rollback plan

### Deploy to Staging
```bash
# 1. Deploy files
cp app/services/ingestion_service.py.new app/services/ingestion_service.py
cp app/retrieval/hybrid.py.new app/retrieval/hybrid.py
cp app/orchestrator/rag.py.new app/orchestrator/rag.py

# 2. Restart staging service
systemctl restart enterprise-rag-staging
```

### Verify Code Deployed
- [ ] Check file checksums match
- [ ] Verify no syntax errors in Python files
- [ ] Confirm service started successfully
- [ ] Check application logs for errors

### Run Regression Tests
```bash
# Run Phase 0 specific tests
pytest tests/test_phase0_retrieval_bug_fix.py -v

# Expected output:
#   test_phase0_document_name_fix PASSED
#   test_phase0_kb_isolation PASSED
```

- [ ] Both regression tests PASS
- [ ] No assertion errors
- [ ] Document test output

### Test KB Isolation Manually
- [ ] Upload 2 files to KB1 (different content)
- [ ] Upload 2 files to KB2 (different content)
- [ ] Query KB1 → verify only KB1 files retrieved
- [ ] Query KB2 → verify only KB2 files retrieved
- [ ] Query all KBs → verify both KBs' files retrieved
- [ ] Confirm no cross-KB contamination

### Run Reindex Script (Testing)
```bash
# Preview with --limit 5
python scripts/reindex_all_uploads.py --limit 5 --dry-run

# Expected output:
#   [DRY-RUN] Would delete vectors for upload ...
#   [DRY-RUN] Would re-ingest from ...
```

- [ ] Dry-run completes without errors
- [ ] Review what would be reindexed
- [ ] Document reindex time estimate

### Run Full Regression Suite
```bash
# Run all tests to ensure no regressions
pytest tests/ -v
```

- [ ] All tests PASS
- [ ] No PDF/DOCX/PPTX retrieval regressions
- [ ] No auth/permission regressions
- [ ] Document test results

### Performance Baseline on Staging
- [ ] Run 10 KB-scoped queries → measure latency
- [ ] Compare to pre-deployment baseline
- [ ] Confirm performance same or better
- [ ] Document metrics

### Final Staging Approval
- [ ] QA sign-off complete
- [ ] No blockers identified
- [ ] All tests passing
- [ ] Performance acceptable
- [ ] Ready for production deployment

---

## Production Deployment

### Pre-Deployment
- [ ] Schedule maintenance window (if needed)
- [ ] Notify support team
- [ ] Take production backup
- [ ] Record current metrics
- [ ] Prepare rollback procedure
- [ ] Have 2 engineers on standby

### Deploy to Production
```bash
# 1. Deploy files (use your deploy process)
# 2. Verify files deployed correctly
# 3. Restart service

# Your deployment command here:
# ___________________________________
```

- [ ] Deployment completed successfully
- [ ] No errors in startup logs
- [ ] Service responding normally

### Verify Production Deployment
```bash
# Check files are deployed
ls -la app/services/ingestion_service.py
ls -la app/retrieval/hybrid.py
ls -la app/orchestrator/rag.py

# Check service health
curl http://localhost:8000/health
```

- [ ] Files deployed to correct locations
- [ ] Service health check passes
- [ ] No errors in application logs

### Run Production Regression Tests
```bash
# Run Phase 0 tests on production
pytest tests/test_phase0_retrieval_bug_fix.py -v --env=production
```

- [ ] Both tests PASS on production
- [ ] No failures or errors
- [ ] Document results

### Execute Production Reindex

**CRITICAL STEP:** Reindex must run after code deployment

```bash
# Option 1: Full reindex (may take 10-30 minutes)
python scripts/reindex_all_uploads.py

# Option 2: Specific KB reindex
python scripts/reindex_all_uploads.py --kb-id <kb_uuid>

# Option 3: Preview before running
python scripts/reindex_all_uploads.py --dry-run
```

- [ ] Start reindex script
- [ ] Monitor progress in logs
- [ ] Reindex completes successfully
- [ ] Document reindex time
- [ ] Confirm all uploads reindexed

### Monitor Post-Deployment

**First Hour:**
- [ ] Check application logs every 5-10 minutes
- [ ] Watch for KB filtering errors
- [ ] Monitor retrieval latency
- [ ] Check error rates

**First 24 Hours:**
- [ ] Daily: Review logs for issues
- [ ] Daily: Spot-check KB isolation working
- [ ] Daily: Monitor performance metrics
- [ ] Daily: Confirm no filtering regressions

- [ ] No critical errors in first hour
- [ ] KB filtering working as expected
- [ ] Performance stable or improved
- [ ] Users reporting improvement

### Production Sign-Off
- [ ] Deployment successful
- [ ] All tests passing
- [ ] Reindex complete
- [ ] 24-hour monitoring complete
- [ ] No regressions
- [ ] Ready for normal operations

---

## Rollback Procedure (If Needed)

### Decision Point
- [ ] Decide rollback is necessary (critical KB filtering failure, etc.)
- [ ] Notify team immediately

### Execute Rollback
```bash
# 1. Revert files to previous version
git checkout HEAD~1 -- app/services/ingestion_service.py
git checkout HEAD~1 -- app/retrieval/hybrid.py
git checkout HEAD~1 -- app/orchestrator/rag.py

# 2. Restart service
systemctl restart enterprise-rag

# 3. Verify rollback
pytest tests/ -v
```

- [ ] Files reverted to previous version
- [ ] Service restarted successfully
- [ ] Tests pass after rollback
- [ ] KB filtering works (previous behavior)
- [ ] File issue with details of why rollback was needed

### Post-Rollback
- [ ] Root cause analysis
- [ ] Code review of issue
- [ ] Fix and re-test locally
- [ ] Prepare for re-deployment

---

## Verification Checklist

### Functional Verification
- [ ] KB1 query returns KB1 files only
- [ ] KB2 query returns KB2 files only
- [ ] "All KBs" query returns both
- [ ] document_name in vectors is correct filename (not UUID)
- [ ] upload_id in vectors is correct upload ID
- [ ] No cross-KB data leakage
- [ ] No permission bypass vulnerabilities

### Performance Verification
- [ ] Retrieval latency: baseline or better
- [ ] KB filtering latency: baseline or better
- [ ] Memory usage: stable
- [ ] CPU usage: stable
- [ ] Database queries: same count as before

### Quality Verification
- [ ] All regression tests pass
- [ ] No new error types in logs
- [ ] No warnings about deprecated functionality
- [ ] Logging working correctly
- [ ] Monitoring metrics collecting data

### Security Verification
- [ ] No SQL injection vectors
- [ ] KB isolation enforced at retrieval level
- [ ] No permission bypass possible
- [ ] Authentication/authorization unchanged

---

## Communication Checklist

### Before Deployment
- [ ] Notify engineering team
- [ ] Notify DevOps team
- [ ] Notify QA team
- [ ] Schedule production deployment
- [ ] Brief support team

### During Deployment
- [ ] Post to #deployments channel
- [ ] Provide status updates every 15 minutes
- [ ] Alert if issues encountered

### After Deployment
- [ ] Announcement to product team
- [ ] Update status in documentation
- [ ] Brief support team on changes
- [ ] Schedule retrospective if issues found

---

## Final Checklist

### All Systems Ready?
- [ ] Code changes reviewed and approved
- [ ] Regression tests pass (staging)
- [ ] Regression tests pass (production)
- [ ] Reindex script completes
- [ ] Performance verified
- [ ] KB isolation confirmed
- [ ] 24-hour monitoring complete
- [ ] No critical issues

### Ready for Next Phase?
- [ ] PHASE 0 fully deployed and stable
- [ ] All acceptance criteria met
- [ ] Team has capacity for PHASE 1
- [ ] PHASE 1 prerequisites understood
- [ ] PHASE 1 timeline communicated

---

## Document Tracking

- Checklist Version: 1.0
- Created: 2026-08-11
- Last Updated: 2026-08-11
- Status: READY FOR USE

---

## Sign-Off

**Deployment Completed By:** _______________  
**Date:** _______________  
**Status:** ✅ APPROVED FOR NEXT PHASE

**QA Sign-Off:** _______________  
**Date:** _______________

**DevOps Sign-Off:** _______________  
**Date:** _______________

---

## Quick Reference Commands

### Run Phase 0 Tests
```bash
pytest tests/test_phase0_retrieval_bug_fix.py -v
```

### Run Full Regression Suite
```bash
pytest tests/ -v
```

### Dry-Run Reindex (Preview)
```bash
python scripts/reindex_all_uploads.py --dry-run
```

### Reindex All Uploads
```bash
python scripts/reindex_all_uploads.py
```

### Reindex Specific KB
```bash
python scripts/reindex_all_uploads.py --kb-id <kb_uuid>
```

### Reindex with Limit (for testing)
```bash
python scripts/reindex_all_uploads.py --limit 5
```

### Check Service Health
```bash
curl http://localhost:8000/health
```

### Monitor Application Logs
```bash
tail -f logs/app.log
```

### Rollback Code
```bash
git checkout HEAD~1 -- app/services/ingestion_service.py app/retrieval/hybrid.py app/orchestrator/rag.py
systemctl restart enterprise-rag
```
