# Test Suite SOP — ServiceNow xMatters Escalation Bridge

**Product:** sn_xmatters_escalation_bridge  
**Author:** Vladimir Kapustin  
**License:** AGPL-3.0  
**Date:** 2026-06-01  

---

## Purpose

This SOP (Standard Operating Procedure) defines the complete test plan for the ServiceNow xMatters Escalation Bridge. Every scenario must pass before a release is approved. The test suite validates correctness of ServiceNow REST API interaction, data processing pipeline, report generation, CLI behavior, and error recovery.

---

## Test Environment

| Requirement | Specification |
|-------------|--------------|
| Python | 3.10+ |
| Test framework | pytest ≥7.0 |
| External dependencies | None (all tests self-contained with `unittest.mock`) |
| ServiceNow instance | Not required (mocked HTTP responses) |
| Network access | Not required (all calls intercepted) |
| Filesystem | Write access to temporary directory (via `tempfile`) |

---

## Run Command

```bash
python3 -m pytest tests/test_engine.py -v
```

---

## Test Scenarios

Total: **15 scenarios** (T01–T15), including 4 negative cases.

---

### T01: Successful Fetch — Single Record

**Purpose:** Verify `Engine.fetch()` correctly parses a valid JSON response from the ServiceNow REST API.

**Input:** Mock response `{"result": [{"sys_id": "abc123", "name": "Test Incident"}]}`  
**Expected:** Returns `[{"sys_id": "abc123", "name": "Test Incident"}]` — list with 1 record  
**Mock:** `requests.get` returns `MagicMock(status_code=200, json=lambda: {"result": [...]})`  
**Category:** Happy path — core functionality

---

### T02: Empty Table — Zero Records

**Purpose:** Verify graceful handling when target table has no records.

**Input:** Mock response `{"result": []}`  
**Expected:** Returns `[]` (empty list) — no crash, no exception  
**Mock:** `requests.get` returns `MagicMock(status_code=200, json=lambda: {"result": []})`  
**Category:** Edge — empty data

---

### T03: Network Error — Exception Raised

**Purpose:** Verify fetch returns empty list on network failure rather than crashing.

**Input:** `requests.get` raises `Exception("Connection refused")`  
**Expected:** Returns `[]` — exception caught, no propagation  
**Mock:** `requests.get` side_effect `Exception("Connection refused")`  
**Category:** Negative — error recovery

---

### T04: Process Normalization — 150 Records Capped at 50

**Purpose:** Verify `Engine.process()` caps output at 50 items regardless of input count.

**Input:** 150 mock records (each `{"sys_id": f"s{i}"}`)  
**Expected:** `{"total": 150, "items": [...50 items...]}` — total reflects all records, items capped  
**Mock:** No external calls; pure data transformation  
**Category:** Boundary — data limits

---

### T05: JSON Report Generation — Structural Integrity

**Purpose:** Verify JSON report is valid, contains expected data, and is written to the correct path.

**Input:** `{"total": 1, "items": [{"name": "X"}]}`, prefix=`"report"`  
**Expected:** File `report.json` exists; valid JSON; `json.load(fp)["total"] == 1`  
**Filesystem:** Uses `tempfile.TemporaryDirectory()`  
**Category:** Happy path — output

---

### T06: Markdown Report Generation — Content Verification

**Purpose:** Verify Markdown report contains item names and correct total count.

**Input:** `{"total": 1, "items": [{"name": "X"}]}`, prefix=`"report"`  
**Expected:** File `report.md` exists; contains string `"X"`; contains `"**Total:** 1"`  
**Filesystem:** Uses `tempfile.TemporaryDirectory()`  
**Category:** Happy path — output

---

### T07: CLI Invocation — Exit Code Check

**Purpose:** Verify CLI runs without argparse error when all required flags are provided.

**Input:** `python3 src/cli.py --sn-url https://dev123.service-now.com --sn-user admin --sn-pass pass`  
**Expected:** Exit code `0` (success), NOT `2` (argparse error)  
**Execution:** Uses `subprocess.run()` with `capture_output=True`  
**Category:** Happy path — CLI integration

---

### T08: HTTP 401 — Unauthorized Access

**Purpose:** Verify fetch handles HTTP 401 without crashing or exposing auth details.

**Input:** Mock response `status_code=401, text="Unauthorized"`  
**Expected:** Returns `[]` — error caught, no exception, no auth data in response  
**Mock:** `requests.get` returns `MagicMock(status_code=401)` (no `raise_for_status` call — current engine calls it but catches Exception)  
**Category:** Negative — auth failure

---

### T09: HTTP 500 — Server Error

**Purpose:** Verify fetch handles internal server error gracefully.

**Input:** Mock response `status_code=500, text="Internal Server Error"`  
**Expected:** Returns `[]` — server error treated as non-fatal  
**Mock:** `requests.get` returns `MagicMock(status_code=500)`  
**Category:** Negative — upstream failure

---

### T10: Empty Items Array in Process

**Purpose:** Verify `process()` handles empty items list without crash.

**Input:** `[]` (empty list of records)  
**Expected:** `{"total": 0, "items": []}` — zero total, empty items array  
**Mock:** No external calls  
**Category:** Edge — empty input

---

### T11: Report Overwrite — Second Run on Same Prefix

**Purpose:** Verify second report generation replaces existing files without errors.

**Input:** Run `report()` twice on same prefix in same temp directory  
**Expected:** Both runs succeed; second run overwrites first; final file contains second run's data  
**Filesystem:** Uses `tempfile.TemporaryDirectory()`  
**Category:** Edge — idempotency

---

### T12: Unicode Field Names — UTF-8 Handling

**Purpose:** Verify reports handle Unicode characters in ServiceNow field names/values.

**Input:** `{"total": 1, "items": [{"name": "Incidente de Red — ネットワーク障害"}]}`  
**Expected:** JSON file contains UTF-8 characters intact; Markdown file renders them correctly  
**Filesystem:** Uses `tempfile.TemporaryDirectory()`  
**Category:** Edge — internationalization

---

### T13: Missing Required --sn-url Flag

**Purpose:** Verify CLI rejects invocation without required `--sn-url` argument.

**Input:** `python3 src/cli.py --sn-user admin --sn-pass pass` (NO `--sn-url`)  
**Expected:** Exit code `2` (argparse error); stderr contains "required"  
**Execution:** Uses `subprocess.run()`  
**Category:** Negative — missing arguments

---

### T14: Invalid URL Format

**Purpose:** Verify fetch handles malformed URL without catastrophic failure.

**Input:** Engine initialized with `sn_url="not-a-valid-url"`  
**Expected:** Fetch runs without crash; returns `[]` on connection error (requests raises `InvalidURL` → caught by `except Exception`)  
**Mock:** Not needed — `requests.get("not-a-valid-url/...")` will naturally fail  
**Category:** Negative — malformed input

---

### T15: Large Payload — 50 Records with 30+ Fields Each

**Purpose:** Verify process handles records with many fields without truncation or memory issues.

**Input:** 50 records, each with 35 fields (simulating complex ServiceNow table schema)  
**Expected:** All 50 records present in `items`; all fields preserved in JSON output; no memory error  
**Mock:** Generate records programmatically  
**Category:** Boundary — data volume

---

## Test Execution Order

```
T01 → T02 → T03 → T10  (fetch + process basics)
T04 → T15               (boundary conditions)
T05 → T06 → T11 → T12   (report generation)
T07 → T13               (CLI integration)
T08 → T09 → T14         (error/negative cases)
```

---

## Pass Criteria

| Criterion | Threshold |
|-----------|-----------|
| Total scenarios | 15/15 must pass |
| Happy path (T01, T05, T06, T07) | 4/4 must pass |
| Negative (T03, T08, T09, T13, T14) | 5/5 must pass |
| Edge/Boundary (T02, T04, T10, T11, T12, T15) | 6/6 must pass |
| Runtime | All 15 tests complete < 10 seconds |
| Memory | No leaks > 10MB during test execution |

---

## Failure Protocol

1. **Isolate failing test:** Run individually with `pytest tests/test_engine.py::test_name -v`
2. **Check mock correctness:** Verify mock response matches expected ServiceNow API format
3. **Check source code:** Has `raise_for_status()` been added without corresponding try/except?
4. **Check dependencies:** Is `requests` installed? (`pip install requests`)
5. **Log evidence:** Capture full pytest output with `--tb=long`
6. **Re-run all:** After fix, run full suite before declaring resolved
