# Edge Cases — ServiceNow xMatters Escalation Bridge

**Product:** sn_xmatters_escalation_bridge  
**Author:** Vladimir Kapustin  
**License:** AGPL-3.0  
**Date:** 2026-06-01  

---

## Purpose

This document catalogs edge cases — boundary conditions, unusual inputs, and corner-case scenarios that the bridge must handle gracefully. Each case includes the scenario, expected behavior, and verification method.

---

## Edge Cases

Total: **14 cases** (E01–E14)

---

### E01: Empty Table — Zero Records Returned

**Scenario:** Target ServiceNow table has no records (e.g., empty `incident` table on fresh instance).  
**Expected:** `fetch()` returns `[]`; `process()` returns `{"total": 0, "items": []}`; reports generated with zero totals.  
**Risk:** Crash on empty iterator, division by zero in report calculations.  
**Verification:** T02 (test suite SOP).

---

### E02: 10,000+ Records — Pagination Boundary

**Scenario:** Table has 10,000+ records, exceeding single `sysparm_limit=100` response.  
**Expected:** Only first 100 records fetched (current design). Future enhancement: support `sysparm_offset` for pagination.  
**Risk:** Silent data loss — user unaware that only subset was fetched.  
**Verification:**
```python
# Mock responses simulate paginated data
# Verify warning printed when result count == limit
```

---

### E03: Null Values in ServiceNow Fields

**Scenario:** ServiceNow record has fields with `null`/`None` values (e.g., `{"assigned_to": null, "priority": null}`).  
**Expected:** Report includes `null` values in JSON; Markdown renders empty or "N/A".  
**Risk:** `i.get('name')` returns `None`; `str(None)` produces "None" in output — confusing to users.  
**Verification:**
```python
data = {"total": 1, "items": [{"name": None, "sys_id": None}]}
e.report(data, "test")
md = open("test.md").read()
assert "None" not in md  # Should use fallback, not literal "None"
```

---

### E04: Unicode and Special Characters

**Scenario:** Field values contain Unicode (Cyrillic, CJK, emoji, RTL text), control characters (`\n`, `\t`), or HTML entities.  
**Expected:** JSON handles all Unicode natively; Markdown escapes or renders correctly.  
**Risk:** `UnicodeEncodeError` if file opened without `encoding="utf-8"`; control chars break JSON syntax.  
**Verification:** T12 (test suite SOP).

---

### E05: ServiceNow Instance Behind VPN/Proxy

**Scenario:** Bridge runs on a machine that requires VPN or proxy to reach ServiceNow instance.  
**Expected:** `requests` honors `HTTP_PROXY`/`HTTPS_PROXY` environment variables automatically.  
**Risk:** No explicit proxy support configured — relies on implicit `requests` env-var behavior.  
**Verification:**
```bash
export HTTPS_PROXY=http://proxy:8080
python3 src/cli.py --sn-url https://dev --sn-user admin --sn-pass pass
# Should route through proxy; if proxy unreachable, returns [] gracefully
```

---

### E06: Extremely Long Field Values (>10KB per field)

**Scenario:** ServiceNow field contains 100KB+ text (e.g., `description` field with log dump).  
**Expected:** Report includes full value; JSON file may be large but valid; no truncation.  
**Risk:** Memory exhaustion if many large records processed simultaneously; report file too large for downstream consumers.  
**Verification:**
```python
big_value = "x" * 100000
data = {"total": 1, "items": [{"description": big_value}]}
e.report(data, "test")
assert len(open("test.json").read()) > 100000
```

---

### E07: Concurrent Requests — Rate Limiting (HTTP 429)

**Scenario:** ServiceNow rate-limits the bridge after rapid successive calls.  
**Expected:** `fetch()` encounters HTTP 429, caught by `except Exception`, returns `[]`.  
**Risk:** Silent failure indistinguishable from other errors — user unaware of rate limiting.  
**Verification:**
```python
with patch("src.engine.requests.get", return_value=MagicMock(status_code=429)):
    result = e.fetch("incident")
    assert result == []
```

---

### E08: ServiceNow Instance Redirect (HTTP 301/302)

**Scenario:** ServiceNow URL redirects to another host (e.g., load balancer, instance migration).  
**Expected:** `requests` follows redirects by default; final URL logged somewhere (currently not).  
**Risk:** Redirect to unexpected host; basic auth credentials sent to redirected host (security concern).  
**Verification:**
```python
with patch("src.engine.requests.get") as mock:
    mock.return_value = MagicMock(status_code=200, json=lambda: {"result": []}, 
                                   history=[MagicMock(status_code=302)])
    result = e.fetch("incident")
    assert result == []
```

---

### E09: Timeout on Slow ServiceNow Instance

**Scenario:** ServiceNow instance responds slowly (30s+); `timeout=30` reached.  
**Expected:** `requests.get` raises `Timeout` or `ConnectionError`; caught by `except Exception`; returns `[]`.  
**Risk:** CLI appears hung; user hits Ctrl+C, leaving partial output.  
**Verification:**
```python
with patch("src.engine.requests.get", side_effect=requests.exceptions.Timeout):
    result = e.fetch("incident")
    assert result == []
```

---

### E10: Output Directory Not Writable

**Scenario:** Current working directory is read-only; `open(f"{prefix}.json", "w")` fails with `PermissionError`.  
**Expected:** Currently crashes (unhandled). Fix: Wrap `open()` in try/except; fall back to `/tmp/` directory.  
**Risk:** CLI crashes with traceback; no report generated; user loses all work.  
**Verification:**
```bash
cd /root && python3 /tmp/sn_xmatters_escalation_bridge/src/cli.py ...
# Expected: permission error printed; graceful exit
```

---

### E11: JSON with Non-Serializable Types

**Scenario:** ServiceNow returns a field with `datetime` object or `Decimal` type (not raw JSON).  
**Expected:** `json.dump()` raises `TypeError`; current code has no `default=` handler.  
**Risk:** Pipeline crashes mid-report after successful fetch — wasted API call.  
**Verification:**
```python
import datetime
data = {"total": 1, "items": [{"opened_at": datetime.datetime.now()}]}
# Expected: graceful serialization (convert to string or skip field)
```

---

### E12: `--output` Prefix Contains Directory Separator

**Scenario:** User specifies `--output /tmp/reports/incidents` (path with directories).  
**Expected:** `open(f"{prefix}.json", "w")` fails with `FileNotFoundError` (parent dir doesn't exist).  
**Risk:** `os.makedirs()` not called before `open()` — directory creation is user's responsibility.  
**Verification:**
```bash
python3 src/cli.py ... --output "/tmp/nonexistent/report"
# Expected: error message about missing directory (not cryptic traceback)
```

---

### E13: ServiceNow API Response Missing `result` Key

**Scenario:** ServiceNow returns `{"error": {"message": "..."}}` instead of `{"result": [...]}`.  
**Expected:** `r.json().get("result", [])` returns `[]` — graceful fallback.  
**Risk:** If `r.json()` returns dict without "result" key, `.get("result", [])` correctly returns `[]`. Already handled.  
**Verification:** Already covered by design (`dict.get` with default).

---

### E14: Python Version Mismatch — f-strings with Variables

**Scenario:** Code uses f-string syntax compatible with Python 3.10+; run on Python 3.9 fails.  
**Expected:** `SyntaxError` on import; clear error message needed.  
**Risk:** Cryptic error for users on older Python.  
**Verification:**
```bash
docker run python:3.9 python3 -c "from src.engine import Engine"
# Expected: SyntaxError with line number; README clearly states 3.10+ requirement
```

---

## Edge Case Priority Matrix

| Priority | Count | Cases |
|----------|-------|-------|
| P0 (Crash) | 3 | E10 (permission), E11 (serialization), E14 (Python version) |
| P1 (Data loss/Silence) | 5 | E02 (pagination), E03 (null values), E07 (rate limit), E08 (redirect), E09 (timeout) |
| P2 (UX/Edge) | 6 | E01 (empty), E04 (unicode), E05 (proxy), E06 (large fields), E12 (path), E13 (missing key) |

---

## Automated Edge Case Coverage

```python
# tests/test_edge_cases.py — placeholder for future edge case automation
def test_e01_empty_table():
    assert e.process([]) == {"total": 0, "items": []}

def test_e03_null_values():
    data = {"total": 1, "items": [{"name": None, "sys_id": None}]}
    e.report(data, "test")
    assert os.path.exists("test.json")
    # Verify no "None" string in markdown

def test_e13_missing_result_key():
    with patch("src.engine.requests.get", 
               return_value=MagicMock(status_code=200, json=lambda: {"error": "msg"})):
        result = e.fetch("incident")
        assert result == []
```
