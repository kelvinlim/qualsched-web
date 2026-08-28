# QualSched Web

Web port of [QualSched](https://github.com/kelvinlim/qualsched) — a researcher UI for
scheduling Qualtrics EMA invitations. **Version 0.1.0**.

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
| Ships as a laptop app | Compose locally; Quadlets on lnpitask (`/qualsched`) |

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
| `SUPERADMIN_EMAILS` | Comma-separated bootstrap researcher emails (superusers on first login) |
| `ALLOWED_EMAIL_DOMAINS` | Comma-separated domains auto-provisioned as regular researchers (`umn.edu` on lnpitask; do not add `gmail.com`) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Optional Google researcher login |
| `RESEARCHER_OAUTH_REDIRECT_URI` | Must match the Cloud Console redirect (local: `http://localhost:8040/auth/callback`; prod: `https://lnpitask.umn.edu/qualsched/auth/callback`) |
| `PUBLIC_PATH_PREFIX` | Host path prefix (`/qualsched` on lnpitask). Backend routes stay unprefixed; host nginx strips it |
| `ENVIRONMENT` | `dev` allows the documented bypass when Google ids are unset; `prod` on lnpitask |

Google tokens are **not** stored. The grant is only used to prove identity against the
allowlist: a `users` row, `SUPERADMIN_EMAILS`, or `ALLOWED_EMAIL_DOMAINS` (campus
`@umn.edu` on lnpitask). Gmail is not included in the domain list. After changing
`.env`, restart the backend.

## Production (lnpitask.umn.edu)

Same host as wearable-hub: Podman **Quadlets** + host nginx location blocks —
not compose. **Different** schema (`qualsched`, not `wearable_hub`), host ports
**8050** / **8060** (loopback; tictech already uses 8030/8040), path prefix
**`/qualsched`** only. Do not occupy `/wearable`, `/enroll`, `/webhooks`,
`/qualtrics_dashboard`, `/tictech`, or port 8000.

Public URL: **https://lnpitask.umn.edu/qualsched/**

Host checklist (do this on lnpitask; full detail in [deploy/README.md](deploy/README.md)):

1. Checkout at `/home/kolim/Projects/qualsched-web` (or edit the Quadlet `EnvironmentFile` path).
2. `cp .env.sample .env` and set `FERNET_KEY`, `SUPERADMIN_EMAILS`,
   `DATABASE_URL` → cnc3 `qualsched`, `DB_WAIT_HOST=cnc3.med.umn.edu`,
   `PUBLIC_PATH_PREFIX=/qualsched`, `ALLOWED_EMAIL_DOMAINS=umn.edu`,
   `RESEARCHER_OAUTH_REDIRECT_URI=https://lnpitask.umn.edu/qualsched/auth/callback`,
   `ENVIRONMENT=prod`. Never commit `.env`.
3. Provision schema/user `qualsched` on cnc3 (Kelvin). No MariaDB container on lnpitask.
4. Add the Google redirect URI above to the OAuth 2.0 web client in GCP project
   `fitbitdata-499001` (same client as wearable-hub).
5. Copy [deploy/quadlet/](deploy/quadlet/) to `/etc/containers/systemd/`
   (`qualsched.network`, backend, frontend — **no scheduler**).
6. Merge [deploy/nginx/qualsched.conf](deploy/nginx/qualsched.conf) into the
   existing TLS `server { }` (do not add a second listen/ssl block).
   `sudo nginx -t && sudo nginx -s reload`.
7. `scripts/deploy.sh` (rebuilds images, restarts units, curls
   `localhost:8050/health` and `localhost:8060/`).

Quadlet sources: [deploy/quadlet/](deploy/quadlet/). Logs:
`sudo journalctl -u qualsched-backend.service -f`.
`docker-compose.yml` is local development only.

## License

MIT. Same as QualSched desktop. Copyright (c) 2026 Kelvin O. Lim.
