# sn_xmatters_escalation_bridge — Risk Report

**Product:** ServiceNow xMatters Escalation Bridge  
**Date:** 2026-06-01  
**Author:** Vladimir Kapustin  

---

## Risk Matrix

| ID | Severity | Category | Risk | Impact | Probability | Mitigation |
|----|----------|----------|------|--------|-------------|------------|
| R01 | **P0** | Security | Credentials exposed via CLI args visible in process list (`ps aux`) | Credential theft on shared systems | High | Read from env vars or `.env` file instead |
| R02 | **P0** | Network | ServiceNow instance unreachable (network partition, VPN down) | Complete failure — no reports generated | Medium | Implement retry with exponential backoff (3 attempts, 5s/10s/20s) |
| R03 | **P1** | Auth | ServiceNow user deactivated or password rotated | Silent failure (returns `[]`) indistinguishable from empty table | Low | Distinguish auth errors (HTTP 401) from empty results; exit with non-zero code |
| R04 | **P1** | Data | Target table has 10M+ records, `sysparm_limit=100` misses data | Incomplete reports; silent data loss | Medium | Add `--limit` CLI flag; warn when total > limit |
| R05 | **P1** | Output | Output directory not writable; report generation fails | Unhandled `IOError`, no partial output saved | Low | Validate write permissions before fetch; use tempfile fallback |
| R06 | **P2** | Performance | 100-record fetch exceeds 30s timeout on slow instances | Pipeline hangs; CLI appears frozen | Low | Reduce timeout to 15s; add progress indicator to CLI |
| R07 | **P2** | Data Integrity | JSON report contains unescaped control characters from ServiceNow fields | Corrupted JSON output; downstream parsers fail | Low | Sanitize output with `json.dumps(ensure_ascii=True)` for known-bad fields |
| R08 | **P2** | Maintainability | `$name` placeholder not replaced in CLI/Engine docstrings | Unprofessional artifact visible in `--help` | Certain | Replace with actual product name in all source files |
| R09 | **P3** | Compatibility | Python 3.10 `str | None` type syntax unsupported on older Python | Import error on Python <3.10 | Low | Document minimum Python 3.10 requirement in README |
| R10 | **P3** | Documentation | `--help` output missing usage examples | User confusion; support burden increases | High | Add `epilog=` with 3 example commands |
| R11 | **P3** | Testing | Tests pass against mock but fail against real ServiceNow instance | False confidence in production readiness | Medium | Add integration test marker; document PDI test procedure |
| R12 | **P2** | Config | Hardcoded `incident` default table may not exist on all instances | CLI runs against non-existent table; returns `[]` | Low | Validate table existence via `sys_db_object` before fetch |
| R13 | **P1** | xMatters | Future xMatters integration introduces second authentication surface | Wider attack surface; more token management | Medium | Use shared credential store; single config file for both platforms |
| R14 | **P3** | CI/CD | No GitHub Actions workflow for automated testing | Manual testing burden; regressions missed | High | Add `.github/workflows/test.yml` with pytest matrix |
| R15 | **P2** | Logging | No structured logging; `print()` only | Hard to debug production failures | Low | Replace `print()` with `logging` module; add `--verbose` flag |

---

## Risk Severity Definitions

| Severity | Response Time | Example |
|----------|--------------|---------|
| **P0** | Immediate (same sprint) | Credential leakage, complete failure to run |
| **P1** | Next sprint | Silent data loss, auth error masking |
| **P2** | Within 2 sprints | Performance degradation, maintainability issues |
| **P3** | Backlog (when convenient) | Documentation gaps, CI/CD absence |

---

## Mitigation Progress

| Status | Count |
|--------|-------|
| Resolved | 0 |
| In Progress | 0 |
| Planned (next sprint) | 5 (R01, R03, R04, R06, R08) |
| Backlog | 10 |

---

## Risk by Phase

### Current (Phase 1 — Planning)
- **R01** (P0): Credential visibility — fix before production use
- **R08** (P2): `$name` placeholders — cosmetic but unprofessional

### Phase 2 (xMatters Integration)
- **R13** (P1): Second auth surface — design shared credential store first

### Production Readiness
- **R11** (P3): Mock-only tests — add integration test suite
- **R14** (P3): No CI/CD — add GitHub Actions
