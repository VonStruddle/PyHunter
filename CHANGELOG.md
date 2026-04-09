# Changelog

## 2.1.0

- Added `AsyncPyHunter` with initial async support for core endpoints:
  - `domain_search`
  - `email_finder`
  - `email_verifier`
  - `email_count`
  - `account_information`
- Hardened sync transport and error handling:
  - timeout/retry/backoff options
  - normalized `HunterApiError` and `HunterTransportError`
  - safer per-call base params (no shared mutation across calls)
- Added pytest test suite including async tests and sync/async parity checks.
- Added GitHub Actions CI for lint, type checks, tests, and coverage threshold.
- Migrated project metadata to `pyproject.toml`.
