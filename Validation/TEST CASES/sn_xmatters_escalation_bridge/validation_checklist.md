# Validation Checklist — ServiceNow xMatters Escalation Bridge

**Product:** sn_xmatters_escalation_bridge  
**Author:** Vladimir Kapustin  
**License:** AGPL-3.0  
**Date:** 2026-06-01  

---

## Purpose

This checklist ensures all quality gates are verified before declaring the product complete. Each item must be checked manually or via automated validation script.

---

## G0: Test Suite SOP Completeness

- [ ] `test_suite_SOP.md` contains ≥10 test scenarios with TXX identifiers
- [ ] Includes negative/corner cases (at least 3 negative scenarios)
- [ ] Each scenario specifies: Purpose, Input, Expected behavior, Mock strategy
- [ ] Scenario count: **15** (T01–T15) — 5 negative, 5 edge/boundary, 5 happy path

---

## G1: Validation Suite Completeness

- [ ] `test_suite_SOP.md` — 15 scenarios (T01–T15)
- [ ] `regression_cases.md` — 10 cases (R01–R10)
- [ ] `edge_cases.md` — 14 cases (E01–E14)
- [ ] `validation_checklist.md` — this document

---

## G2: README Quality

- [ ] Word count ≥2000 (target: 2200+)
- [ ] Mermaid architecture diagram present
- [ ] ROI section with at least 2 calculation tables
- [ ] Troubleshooting section with 8+ diagnostic scenarios
- [ ] Installation instructions (pip/venv)
- [ ] Usage examples (3+ different scenarios)
- [ ] API reference for CLI arguments
- [ ] Security considerations section
- [ ] Testing instructions
- [ ] Roadmap section (xMatters integration)
- [ ] No duplicate section headers (G8 check)

---

## G3: Copyright Headers

- [ ] `src/cli.py` starts with `# Copyright (C) 2026 Vladimir Kapustin` + `# SPDX-License-Identifier: AGPL-3.0-only`
- [ ] `src/engine.py` starts with copyright header (already present: verify)
- [ ] `tests/test_engine.py` starts with copyright header
- [ ] All `.py` files have proper headers

---

## G4: Git Push Verification

- [ ] `git push origin main` succeeds
- [ ] Verify via `curl https://api.github.com/repos/vladarchitectservicenow-oss/sn_xmatters_escalation_bridge/branches/main`
- [ ] Commit appears in branch history

---

## G5: No Hardcoded Credentials

- [ ] `grep -r "password\s*=" src/` — zero literal passwords (env-var reads with `process.env` pattern excluded)
- [ ] `grep -r "api_key\s*=" src/` — zero hardcoded API keys
- [ ] `grep -r "DEFAULT_PASS" src/` — no default passwords
- [ ] CLI credentials use `env:` prefix syntax or `os.environ` fallbacks

---

## G6: .gitignore

- [ ] `.gitignore` exists at repo root
- [ ] Excludes: `__pycache__/`, `*.pyc`, `reports/`, `*.log`, `.env`, `.pytest_cache/`
- [ ] Excludes: IDE artifacts (`.vscode/`, `.idea/`)

---

## G7: License Consistency

- [ ] `LICENSE` file is full AGPL-3.0 text (not SPDX tag alone)
- [ ] README license section header matches `AGPL-3.0-only`
- [ ] All source file SPDX tags match LICENSE

---

## G8: No Duplicate README Headers

- [ ] `grep '^## ' README.md | sort | uniq -d` returns empty
- [ ] Distinct section count: 12–18 unique headers
- [ ] No repeated content blocks

---

## Additional Quality Checks

### Documentation
- [ ] `architecture_summary.md` ≥40 lines with component table, data flow, API contract, benchmarks
- [ ] `dependency_report.md` ≥30 lines with Python deps, platform deps, role requirements, network deps
- [ ] `risk_report.md` ≥10 risk entries with severity tags (P0–P3) and mitigation strategies
- [ ] `execution_plan.md` ≥30 lines with phase breakdown and concrete actions

### Source Code
- [ ] No `$name` placeholder remaining in any source file
- [ ] `--help` output shows correct product name (not `$name`)
- [ ] All functions have docstrings (at minimum: `fetch`, `process`, `report`, `run`)
- [ ] No `print("Report generated.")` as sole output — use structured logging

### Tests
- [ ] `pytest tests/test_engine.py` passes with zero failures
- [ ] Test coverage ≥80% of Engine methods
- [ ] All tests are self-contained (no network calls)
- [ ] Test files have copyright headers

### Security
- [ ] No secrets in commit history (`git log -p | grep -i password`)
- [ ] `.env` not committed to repository
- [ ] HTTPS enforced (no `http://` in production code paths)

### Git
- [ ] `git config user.name "Vladimir Kapustin"`
- [ ] `git config user.email` configured
- [ ] Conventional commit message format (`feat(validation): ...`)
- [ ] `DONE.marker` committed and pushed

---

## Automated Gate Check (quality-gate-checker.py)

```python
# Copy quality-gate-checker.py from skill references into repo root
# Run: python3 quality-gate-checker.py
```

Expected output:
```
G0: PASS (15 TXX scenarios)
G1: PASS (4 validation docs present)
G2: PASS (README 2200+ words, Mermaid, ROI, Troubleshooting)
G3: PASS (3/3 source files with AGPL-3.0 headers)
G4: PASS (branch ref updated)
G5: PASS (no hardcoded credentials)
G6: PASS (.gitignore exists)
G7: PASS (README AGPL-3.0 matches LICENSE)
G8: PASS (zero duplicate headers)
---
ALL GATES PASSED
```

---

## Validation Sign-Off

| Gate | Validator | Date | Result |
|------|-----------|------|--------|
| G0 | Automated | 2026-06-01 | ✓ 15 scenarios |
| G1 | Automated | 2026-06-01 | ✓ 4 docs present |
| G2 | Manual/automated | 2026-06-01 | Pending |
| G3 | Automated grep | 2026-06-01 | Pending |
| G4 | GitHub API | 2026-06-01 | Pending |
| G5 | Automated grep | 2026-06-01 | Pending |
| G6 | File check | 2026-06-01 | Pending |
| G7 | Manual diff | 2026-06-01 | Pending |
| G8 | grep + uniq | 2026-06-01 | Pending |

---

## Failure Protocol

If any gate fails:
1. **Document failure** in this section with timestamp and gate ID
2. **Fix the issue** (patch source, rewrite docs, update README)
3. **Re-verify** the failed gate
4. **Re-run all gates** (some fixes may cascade to other gates)
5. **Update sign-off table** with corrected result
