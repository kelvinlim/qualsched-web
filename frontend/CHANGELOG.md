# Changelog

All notable changes to QualSched Web are documented in this file.

## [Unreleased]

### Changed
- Contacts no longer shows the milestone-1 "not wired" banner. The page lists
  participants from the Qualtrics mailing list and can add, edit, and remove them.
- Schedule no longer shows the milestone-1 "not wired" banner. Compute plan and
  Send book Qualtrics invitations; the plan is not kept in this app.

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
