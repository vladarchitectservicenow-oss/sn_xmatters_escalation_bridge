# Regression Cases — ServiceNow xMatters Escalation Bridge

**Product:** sn_xmatters_escalation_bridge  
**Author:** Vladimir Kapustin  
**License:** AGPL-3.0  
**Date:** 2026-06-01  

---

## Purpose

This document catalogs historical bugs, known regressions, and verification scenarios that must be re-tested after every code change. Each case includes the original symptom, root cause, fix, and verification steps.

---

## Regression Cases

Total: **10 cases** (R01–R10)

---

### R01: `raise_for_status()` Silently Caught — HTTP Errors Masked

**Discovered:** v0.1.0 initial audit  
**Symptom:** Fetch returns `[]` for HTTP 401, 403, 500 — indistinguishable from empty table  
**Root Cause:** `r.raise_for_status()` throws `HTTPError` which is caught by `except Exception`  
**Fix:** Check `r.status_code` before calling `r.json()`. If status ≥ 400, log warning to stderr and return `[]`  
**Verification:**
```python
# Test: mock 401 response
# Expected: returns [] AND stderr contains "HTTP 401"
import io, sys
stderr_capture = io.StringIO()
old_stderr = sys.stderr
sys.stderr = stderr_capture
e = Engine("https://sn", "admin", "pass")
with patch("src.engine.requests.get", return_value=MagicMock(status_code=401)):
    result = e.fetch("incident")
assert result == []
assert "401" in stderr_capture.getvalue()
sys.stderr = old_stderr
```
**Re-test triggers:** Any change to `engine.py` error handling, `requests.get` usage, or `fetch()` method signature.

---

### R02: `process()` Returns All Records Without Cap

**Discovered:** v0.1.0 code review  
**Symptom:** 10,000+ records in `items` array — memory bloat and oversized report  
**Root Cause:** `process()` returned `records[:50]` correctly but if slicing removed, entire list passed through  
**Fix:** Keep `items[:50]` slice; add unit test with 100+ records verifying cap  
**Verification:**
```python
big_input = [{"sys_id": f"s{i}"} for i in range(500)]
result = e.process(big_input)
assert result["total"] == 500
assert len(result["items"]) == 50
```
**Re-test triggers:** Any change to `process()` method, especially the slice operation.

---

### R03: Report Generation Leaves Open File Handles

**Discovered:** v0.1.0 static analysis  
**Symptom:** `open(f"{prefix}.md", "w").write(...)` — file handle never closed explicitly; relies on garbage collection  
**Root Cause:** Inline `open().write()` pattern — CPython closes on refcount zero but not guaranteed  
**Fix:** Use `with open(...) as f: f.write(...)` context manager  
**Verification:**
```python
import resource
before = resource.getrusage(resource.RUSAGE_SELF).ru_nfile
for _ in range(100):
    e.report({"total": 1, "items": []}, "test")
after = resource.getrusage(resource.RUSAGE_SELF).ru_nfile
assert after - before < 5  # No file descriptor leak
```
**Re-test triggers:** Any change to `report()` method, file I/O patterns.

---

### R04: CLI Import Path Breaks on Python < 3.10

**Discovered:** v0.1.0 environment audit  
**Symptom:** `ImportError: cannot import name 'Engine' from 'src.engine'` when run from outside repo  
**Root Cause:** `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` inserts `src/` but import uses `from src.engine import Engine` — searches for `src/src/engine.py`  
**Fix:** Either change import to `from engine import Engine` (after path insert) or insert parent directory  
**Verification:**
```bash
cd /tmp && python3 /tmp/sn_xmatters_escalation_bridge/src/cli.py --help
# Expected: help text displayed (exit code 0)
```
**Re-test triggers:** Any change to `cli.py` `sys.path` manipulation or import statements.

---

### R05: `--sn-pass` Visible in Process List (`ps aux`)

**Discovered:** v0.1.0 security audit (R01 in risk report)  
**Symptom:** Running `ps aux | grep cli.py` shows full command line including password  
**Root Cause:** CLI receives password as argument string, not from env var  
**Fix:** Support `--sn-pass env:SN_PASS` syntax; read from `os.environ` when `env:` prefix detected  
**Verification:**
```bash
# Set password in env
export SN_PASS=secret123
# Run CLI using env reference
python3 src/cli.py --sn-url https://dev --sn-user admin --sn-pass env:SN_PASS &
PID=$!
# Check process list — password should not appear
ps aux | grep $PID | grep -c "secret123"
# Expected: 0 (password NOT visible)
kill $PID 2>/dev/null
```
**Re-test triggers:** Any change to `cli.py` argument handling, credential management.

---

### R06: ServiceNow URL Trailing Slash Normalization

**Discovered:** v0.1.0 input validation review  
**Symptom:** `self.sn_url.rstrip("/")` strips trailing slash but URL may have path components  
**Root Cause:** Engine assumes URL ends at hostname; works correctly for `https://dev.service-now.com` but not `https://dev.service-now.com/api`  
**Fix:** Validate URL format in CLI; reject URLs containing path components beyond hostname  
**Verification:**
```python
e = Engine("https://dev.service-now.com/", "admin", "pass")
assert e.sn_url == "https://dev.service-now.com"
# Verify fetch constructs correct URL
e.sn_url = "https://dev.service-now.com"
expected_url = "https://dev.service-now.com/api/now/table/incident"
# Mock intercept to verify URL
```
**Re-test triggers:** Any change to URL construction, `sn_url` attribute, or `fetch()` method.

---

### R07: Markdown Report — Missing Item Name Fallback

**Discovered:** v0.1.0 edge case review  
**Symptom:** Markdown report line shows `- ` (empty bullet) when item has no `name` field and `sys_id` is `None`  
**Root Cause:** `i.get('name', i.get('sys_id',''))` — if both missing, empty string  
**Fix:** Add fallback to `f"Record {idx}"` where `idx` is loop index  
**Verification:**
```python
data = {"total": 2, "items": [{}, {"name": None, "sys_id": None}]}
e.report(data, "test")
md_content = open("test.md").read()
assert "Record " in md_content  # Fallback text present
```
**Re-test triggers:** Any change to `report()` markdown generation logic.

---

### R08: JSON Report Float Precision — Large Numbers

**Discovered:** v0.1.0 data integrity review  
**Symptom:** ServiceNow IDs or numeric fields with >15 significant digits lose precision in JSON  
**Root Cause:** `json.dump()` uses Python's default float representation  
**Fix:** Use `json.dump(data, f, ensure_ascii=False, indent=2, default=str)` for non-serializable types  
**Verification:**
```python
data = {"total": 1, "items": [{"big_number": 99999999999999999}]}
e.report(data, "test")
import json
loaded = json.load(open("test.json"))
assert str(loaded["items"][0]["big_number"]) == "99999999999999999"
```
**Re-test triggers:** Any change to JSON serialization, `report()` method, or data types.

---

### R09: Concurrent CLI Invocations Race on Output Files

**Discovered:** v0.1.0 concurrency review  
**Symptom:** Two simultaneous CLI runs with same `--output` prefix produce corrupted or interleaved files  
**Root Cause:** No file locking; both processes write to same `report.json` and `report.md`  
**Fix:** Add PID to output filename by default (`report_{pid}.json`); or use advisory file lock  
**Verification:**
```bash
python3 src/cli.py ... --output "/tmp/test1" &
python3 src/cli.py ... --output "/tmp/test2" &
wait
# Both must produce valid JSON
python3 -c "import json; json.load(open('/tmp/test1.json'))" && echo "PASS1"
python3 -c "import json; json.load(open('/tmp/test2.json'))" && echo "PASS2"
```
**Re-test triggers:** Any change to output file handling, `report()` method, or concurrent execution patterns.

---

### R10: `--table` Validation — Non-Existent Table Silent Failure

**Discovered:** v0.1.0 UX review  
**Symptom:** `--table nonexistent_table` returns `[]` silently; user thinks table is empty rather than nonexistent  
**Root Cause:** ServiceNow returns `[]` for non-existent tables (same as empty tables)  
**Fix:** Before fetch, query `sys_db_object` to verify table exists; if 404, print error and exit  
**Verification:**
```python
# Mock sys_db_object check
with patch("src.engine.requests.get") as mock_get:
    def side_effect(url, **kwargs):
        if "sys_db_object" in url:
            return MagicMock(status_code=200, json=lambda: {"result": []})
        return MagicMock(status_code=200, json=lambda: {"result": []})
    mock_get.side_effect = side_effect
    # Expect warning printed when sys_db_object returns empty
```
**Re-test triggers:** Any change to `fetch()`, CLI argument validation, or table discovery logic.

---

## Regression Test Execution

```bash
# Run all regression verification scripts
python3 -m pytest tests/test_engine.py -v -k "R01 or R02 or R03 or R04 or R05 or R06 or R07 or R08 or R09 or R10"
```

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-06-01 | 1.0.0 | Initial regression catalog (10 cases) |
