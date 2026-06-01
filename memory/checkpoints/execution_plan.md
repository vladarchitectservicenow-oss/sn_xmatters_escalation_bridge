# sn_xmatters_escalation_bridge — Execution Plan

**Product:** ServiceNow xMatters Escalation Bridge  
**Date:** 2026-06-01  
**Author:** Vladimir Kapustin  
**Status:** Phase 1-2 Execution  

---

## Phase Overview

| Phase | Name | Duration | Output | Dependencies |
|-------|------|----------|--------|-------------|
| 1 | Analysis & Planning | Complete | 4 docs (arch, deps, risks, plan) | None |
| 2 | Validation Suite | In Progress | 4 test docs (SOP, regression, edge, checklist) | Phase 1 |
| 3 | Source Hardening | Pending | Fix R08 (`$name`), R01 (env-var auth), `.gitignore` | Phase 2 |
| 4 | README Expansion | Pending | README ≥2000 words, Mermaid, ROI, Troubleshooting | Phase 3 |
| 5 | Quality Gates | Pending | G0-G8 verification | Phase 4 |
| 6 | Git Push + DONE | Pending | Commit, push, DONE.marker | Phase 5 |

---

## Phase 1: Analysis & Planning (COMPLETE)

### Actions
- [x] Inspect repository structure (16 files, Python 3.10+)
- [x] Identify architecture: CLI → Engine → ServiceNow REST
- [x] Detect framework: pure Python, no framework dependencies
- [x] Write `architecture_summary.md` (data flow, API contract, performance benchmarks)
- [x] Write `dependency_report.md` (Python deps, ServiceNow/xMatters platform deps, roles, network)
- [x] Write `risk_report.md` (15 risks: R01-R15, P0-P3 severity, mitigation strategies, phase tracking)
- [x] Write `execution_plan.md` (this document)

### Findings
- **Engine** is a generic fetch-process-report pipeline; "xMatters" branding not yet implemented
- **Tests** exist (7 test functions) but run against mocks only; no integration tests
- **Source bugs:** `$name` placeholder not replaced in CLI/Engine docstrings (R08)
- **Security gap:** Credentials passed as CLI args, visible in process list (R01)

---

## Phase 2: Validation Suite (IN PROGRESS)

### Actions
- [ ] Write `test_suite_SOP.md` — 10+ scenarios with T01-TXX IDs (negative cases included)
- [ ] Write `regression_cases.md` — 8+ regression entries (R01-R08)
- [ ] Write `edge_cases.md` — edge/boundary conditions
- [ ] Write `validation_checklist.md` — gate-by-gate checklist

### SOP Scenarios (Planned)
1. **T01:** Successful fetch with mock 200 response → 1 record returned
2. **T02:** Empty table (200 OK, result=[]) → process returns total=0
3. **T03:** Network error (requests.get raises Exception) → fetch returns []
4. **T04:** Process normalization — 150 records → capped at 50 items
5. **T05:** JSON report generation → file exists, valid JSON, correct total
6. **T06:** Markdown report generation → file exists, contains item names
7. **T07:** CLI invocation with full args → exit code 0 (not 2)
8. **T08:** HTTP 401 Unauthorized → fetch returns [] (current behavior)
9. **T09:** HTTP 500 Server Error → fetch returns [] (graceful degradation)
10. **T10:** Empty items array in process → total=0, no crash
11. **T11:** Report overwrite — second report on same prefix → file replaced
12. **T12:** Unicode field names — JSON report handles UTF-8 correctly
13. **T13:** Negative: missing required --sn-url → argparse error, exit code ≠ 0
14. **T14:** Negative: invalid URL format → requests throws, handled gracefully
15. **T15:** Large payload — 50+ records, each with 30+ fields → no truncation

---

## Phase 3: Source Hardening (PLANNED)

### Actions
- [ ] Replace `$name` placeholder with actual product name in:
  - `src/cli.py` line 4 (`argparse.ArgumentParser(description="$name")`)
  - `src/engine.py` line 3 (module docstring)
- [ ] Add env-var credential support: `--sn-pass` accepts `env:VAR_NAME` syntax or falls back to `$SN_PASS`
- [ ] Add `.gitignore` with patterns: `__pycache__/`, `*.pyc`, `reports/`, `*.json`, `*.md` (except README), `.env`, `*.log`
- [ ] Add `--help` epilog with 3 usage examples
- [ ] Validate `--table` exists before fetch (optional `--skip-validation` flag)
- [ ] Distinguish HTTP 401 from empty results; print warning on stderr

### Files Modified
- `src/cli.py` — fix `$name`, add env-var support, add epilog, add table validation
- `src/engine.py` — fix `$name`, add auth error detection
- `.gitignore` — new file

---

## Phase 4: README Expansion (PLANNED)

### Target
≥2000 words with:
- Mermaid architecture diagram (data flow)
- ROI analysis (3 tables: time saved, cost avoided, efficiency gains)
- Troubleshooting (8+ scenarios with diagnostic commands)
- Installation instructions
- Usage examples (3+ scenarios)
- API reference
- Security considerations
- Testing instructions
- Roadmap (xMatters integration)
- License section matching LICENSE file (AGPL-3.0)
- No duplicate sections (current README has 13 duplicated headers — must deduplicate)

### Current State
- 2262 words but 13 of 15 headers are duplicated (entire content repeated)
- Has Mermaid diagram (basic)
- Missing: proper ROI tables, troubleshooting with diagnostic commands

---

## Phase 5: Quality Gates (PLANNED)

### Gate Checklist (G0-G8)
| Gate | Rule | Status |
|------|------|--------|
| G0 | `test_suite_SOP.md` ≥10 TXX scenarios | Pending |
| G1 | All validation docs present | Pending |
| G2 | README ≥2000 words, Mermaid + ROI + Troubleshooting | Pending |
| G3 | Every `src/` file has AGPL-3.0 copyright header | Partial: engine.py has it, cli.py missing |
| G4 | Git push verified via API | Pending |
| G5 | No hardcoded credentials (exclude `process.env`) | Check: `--sn-pass` reads from env, PASS |
| G6 | `.gitignore` exists | Pending |
| G7 | README license header matches LICENSE (AGPL-3.0) | Pending |
| G8 | No duplicate README headers | FAIL: 13 duplicates → deduplicate |

---

## Phase 6: Git Push + DONE (PLANNED)

### Actions
- [ ] `git add -A`
- [ ] `git commit -m "feat(validation): complete Phase 1-2 docs, README dedup + expansion, source hardening, .gitignore"`
- [ ] `git push origin main` (with `x-access-token` auth)
- [ ] Verify push via `GET /repos/{owner}/{repo}/branches/main`
- [ ] Create `DONE.marker`
- [ ] Push `DONE.marker`

---

## Timeline

| Milestone | Target | Dependency |
|-----------|--------|------------|
| Phase 1 complete | 2026-06-01 | None |
| Phase 2 complete | 2026-06-01 | Phase 1 |
| Phase 3 complete | 2026-06-01 | Phase 2 |
| Phase 4 complete | 2026-06-01 | Phase 3 |
| Phase 5 complete | 2026-06-01 | Phase 4 |
| Phase 6 complete | 2026-06-01 | Phase 5 |

---

## Risk Log

| Risk ID | Severity | Mitigation Applied |
|---------|----------|-------------------|
| R01 | P0 | Add env-var credential support (Phase 3) |
| R03 | P1 | Distinguish HTTP errors from empty results (Phase 3) |
| R08 | P2 | Replace `$name` placeholders (Phase 3) |
| R14 | P3 | Add `.github/workflows/test.yml` (future sprint) |
