# Changelog

All notable changes to QualSched Web are documented in this file.

## [Unreleased]

### Added
- Contacts screen talks to the Qualtrics mailing list (list, add, edit, remove, fill
  missing embedded defaults). Participant PHI is proxied live and never stored.
- Missing directory ID, mailing list ID, or API token returns HTTP 400 with a clear
  reason instead of an empty list that looks like "no participants."
- Schedule preview and execute: compute a NumDays × TimeSlots plan in each contact's
  timezone and book one Qualtrics distribution per participant × day × slot. The plan
  is not stored. Missing token, data center, directory, mailing list, survey id, or
  message id returns HTTP 400 rather than an empty plan.

### Notes
- Deleting a contact still removes them from the Qualtrics mailing list. Cancelling
  their unsent invitations is not wired yet (Distributions list/delete stay 501), so
  the response reports `cancelled=0`.
- Schedule progress SSE is still a no-op. Distributions list/cancel is next.

## [0.0.1] - 2026-08-27

### Added
- Milestone 1 skeleton: Svelte 5 UI ported from desktop QualSched, FastAPI backend
  patterned on wearable-hub ops (Fernet, Google allowlist, MariaDB).
- Accounts screen stores Qualtrics data-center metadata and a Fernet-encrypted API
  token. The browser never receives the token.
- Survey profile CRUD. Schedule / Distributions are not wired yet; those screens
  stay honest about it.
- Docker Compose: MariaDB + backend `:8030` + frontend `:8040`.
- Documented local dev-login when Google OAuth client ids are unset.
