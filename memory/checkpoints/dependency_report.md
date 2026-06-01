# sn_xmatters_escalation_bridge — Dependency Report

**Product:** ServiceNow xMatters Escalation Bridge  
**Date:** 2026-06-01  
**Author:** Vladimir Kapustin  

---

## Python Runtime Dependencies

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| `requests` | ≥2.28 | HTTP client for ServiceNow REST API calls | Yes |
| `argparse` | stdlib | CLI argument parsing | Yes |
| `json` | stdlib | JSON serialization/deserialization | Yes |
| `sys` | stdlib | System path manipulation | Yes |
| `os` | stdlib | Filesystem operations | Yes |
| `typing` | stdlib | Type hints (List, Dict) | No (dev) |
| `pytest` | ≥7.0 | Test runner for test suite | No (dev) |
| `unittest.mock` | stdlib | Mocking for ServiceNow API responses | No (dev) |

---

## ServiceNow Platform Dependencies

| Dependency | Type | Required | Notes |
|-----------|------|----------|-------|
| ServiceNow Instance (Utah+) | External | Yes | REST Table API endpoint |
| Table API (`/api/now/table/`) | API | Yes | Standard ServiceNow REST API |
| Basic Auth credentials | Auth | Yes | User must have `rest_api` or `admin` role |
| `incident` table (default) | Data | Yes | Configurable via `--table` flag |

---

## xMatters Platform Dependencies (Planned)

| Dependency | Type | Required | Notes |
|-----------|------|----------|-------|
| xMatters On-Demand API | External | Planned | `POST /api/xm/1/events` endpoint |
| xMatters API Key | Auth | Planned | xMatters REST API authentication |
| xMatters Form/Plan | Config | Planned | Target event plan for escalation |

---

## Network Dependencies

| Endpoint | Protocol | Port | Firewall Rule |
|----------|----------|------|--------------|
| `{instance}.service-now.com` | HTTPS | 443 | Outbound allowed |
| `{instance}.xmatters.com` (planned) | HTTPS | 443 | Outbound allowed |

---

## Filesystem Dependencies

| Path | Purpose | Write Required |
|------|---------|---------------|
| `{prefix}.json` | Structured report output | Yes |
| `{prefix}.md` | Human-readable report output | Yes |
| Current working directory | Default output location | Yes |

---

## Test Environment Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Runtime |
| pytest | ≥7.0 | Test discovery and execution |
| tempfile | stdlib | Temporary directory creation for report tests |
| subprocess | stdlib | CLI invocation testing |

---

## Role & Permission Requirements

### ServiceNow User
- **Minimum:** `snc_read_only` or custom role with read access to target table
- **Recommended:** `rest_api` role for full REST API access
- **NOT required:** `admin`, `security_admin`, scoped app access

### Local System
- **Write access** to current working directory
- **Network access** to ServiceNow instance (HTTPS outbound)

---

## Plugin & Activation Dependencies

| Dependency | Required | Notes |
|-----------|----------|-------|
| REST API Plugin (`com.glide.rest`) | Yes | Standard activation on all instances |
| No custom ServiceNow plugins | N/A | Bridge uses standard REST API only |
| No scoped application | N/A | External consumer — no app installation needed |

---

## Breaking Change Risks

1. **ServiceNow API version changes:** Table API is stable across releases (Utah → Australia). Monitor Release Notes.
2. **Authentication changes:** If ServiceNow deprecates Basic Auth, switch to OAuth 2.0.
3. **Table schema changes:** If target table fields change, report output adapts (JSON pass-through).
4. **`requests` library EOL:** Monitor PyPI for security advisories.
