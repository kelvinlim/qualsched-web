# QualSched Web

Web port of [QualSched](https://github.com/kelvinlim/qualsched) — a researcher UI for
scheduling Qualtrics EMA invitations. **Version 0.0.1** (milestone 1 skeleton).

Desktop QualSched stays in its own repo. This app is the hosted version: the same
Svelte screens, a FastAPI backend, MariaDB.

## PHI rule (non-negotiable)

Participant PHI — names, phones, emails, time slots, time zones, LogData — **must stay
in Qualtrics**. The app database never stores contact/participant records.

Allowed tables:

| Table | What it holds |
| --- | --- |
| `users` | Researchers (Google allowlist). Not study participants. |
| `qualtrics_accounts` | Data center, directory id, library id, **Fernet-encrypted** API token |
| `survey_profiles` | Survey id, mailing list id, template ids, sender, default settings |

There is no `contacts` table. No participant phone/email/name columns. Contact
list/create/update/delete and schedule preview/execute proxy Qualtrics and discard
the payload after the response. The plan is never stored.

The Qualtrics API token is encrypted at rest. The browser **never** receives it. The
frontend calls `/api/...`; the backend uses httpx against `{dc}.qualtrics.com`.

## How this differs from desktop QualSched

| Desktop (`kelvinlim/qualsched`) | This repo |
| --- | --- |
| Tauri + local JSON config + OS keychain | FastAPI + MariaDB + Fernet |
| No researcher login | Google OAuth allowlist (wearable-hub pattern) |
| `invoke` / `listen` from the webview | HTTP (SSE later for schedule progress) |
| Native file dialogs | `<input type="file">` and downloads |
| Ships as a laptop app | Compose locally; Quadlets on lnpitask later |

The sidebar and screens are the same: Accounts, Survey profile, Contacts, Schedule,
Distributions, Import, Export, Guide.

**Milestone 1** wires Accounts (save data center + token) and survey-profile CRUD.
Contacts now proxies the Qualtrics mailing list (no local participant table).
Schedule computes a plan and books Qualtrics distributions; the plan is not stored.
Distributions lists booked invitations from Qualtrics and can cancel unsent ones;
removing a contact cancels theirs first.

## How to run (Docker Compose, local MariaDB sidecar)

MariaDB is the intended database. Local compose starts a **sidecar** MariaDB
named `db` (host port **3307**) so you can work offline. That sidecar is not
used on lnpitask — production points at external MariaDB on `cnc3.med.umn.edu`,
same as wearable-hub.

Ports: API **8030**, UI **8040** — they do not collide with wearable-hub
(`8010`/`8020`) or `/qualtrics_dashboard` on `8000`.

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
cp .env.sample .env
# paste the key into FERNET_KEY=
# set SUPERADMIN_EMAILS=you@umn.edu
# compose overrides DATABASE_URL / DB_WAIT_* to the sidecar `db` (see docker-compose.yml)

docker compose up --build
```

The backend entrypoint waits for `DB_WAIT_HOST:DB_WAIT_PORT`, runs
`alembic upgrade head`, then uvicorn. Open http://localhost:8040. Sign in with
the SUPERADMIN_EMAILS address (development sign-in, because Google client ids
are empty). On Accounts: add an account, paste a Qualtrics API token, save.
Reload — the token field stays empty and says it is stored.

### Tests (in-memory SQLite)

From `backend/`: `pytest`. The fixture is in-memory SQLite + `create_all`.
Alembic revision `0001` is what production/compose apply on **MariaDB 11**
(see `backend/tests/test_alembic_mariadb.py`).

SQLite is not the default first-run. An explicit `sqlite:///./qualsched.db` URL
is an escape hatch only (entrypoint skips the network wait for `sqlite*`).

## Environment variables

See [`.env.sample`](.env.sample). Summary:

| Variable | Purpose |
| --- | --- |
| `FERNET_KEY` | Encrypts Qualtrics tokens **and** the session cookie |
| `DATABASE_URL` | `mysql+pymysql://…` — compose sidecar `db`, or cnc3 in prod |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Schema `qualsched` (do not reuse `wearable_hub`) |
| `DB_WAIT_HOST` / `DB_WAIT_PORT` | entrypoint waits here before `alembic upgrade head` |
| `SUPERADMIN_EMAILS` | Comma-separated bootstrap researcher emails |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Optional Google researcher login |
| `RESEARCHER_OAUTH_REDIRECT_URI` | Must match the Cloud Console redirect (local: `http://localhost:8040/auth/callback`) |
| `ENVIRONMENT` | `dev` allows the documented bypass when Google ids are unset; never in prod |

Google tokens are **not** stored. The grant is only used to prove identity against the
allowlist (`users` row or `SUPERADMIN_EMAILS`).

## Production note (lnpitask.umn.edu)

Same host as wearable-hub, **different schema** (`qualsched`, not
`wearable_hub`), ports **8030** / **8040**, path prefix **`/qualsched`**. Do not
occupy `/wearable` or port 8000 (`/qualtrics_dashboard`).

Production `.env` points `DATABASE_URL` at the **external** MariaDB
`cnc3.med.umn.edu:3306/qualsched` (placeholder password in `.env.sample` —
replace it; never commit a real one). There is no MariaDB container on
lnpitask, same as wearable-hub compose. Provision the `qualsched` schema/user
on cnc3 before first start.

Quadlet / host nginx deploy is a later conversation.

## License

MIT. Same as QualSched desktop. Copyright (c) 2026 Kelvin O. Lim.
