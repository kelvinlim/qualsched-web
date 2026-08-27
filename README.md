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

## How to run (Docker Compose)

Preferred. Starts MariaDB, the API on **8030**, and the UI on **8040** — ports chosen so
they do not collide with wearable-hub (`8010`/`8020`) or `/qualtrics_dashboard` on `8000`.

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
cp .env.sample .env
# paste the key into FERNET_KEY=
# set SUPERADMIN_EMAILS=you@umn.edu

docker compose up --build
```

Open http://localhost:8040. Sign in with the SUPERADMIN_EMAILS address (development
sign-in, because Google client ids are empty). On Accounts: add an account, paste a
Qualtrics API token, save. Reload — the token field stays empty and says it is stored.

### SQLite first-run (no MariaDB)

From `backend/`, with a generated `FERNET_KEY` in `.env`:

```bash
export DATABASE_URL=sqlite:///./qualsched.db
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8030
```

In another terminal: `cd frontend && npm install && npm run dev` (Vite on 8040, proxies
`/api` `/auth` `/health` to 8030).

## Environment variables

See [`.env.sample`](.env.sample). Summary:

| Variable | Purpose |
| --- | --- |
| `FERNET_KEY` | Encrypts Qualtrics tokens **and** the session cookie |
| `DATABASE_URL` | `mysql+pymysql://...` (compose) or `sqlite:///./qualsched.db` |
| `SUPERADMIN_EMAILS` | Comma-separated bootstrap researcher emails |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Optional Google researcher login |
| `RESEARCHER_OAUTH_REDIRECT_URI` | Must match the Cloud Console redirect (local: `http://localhost:8040/auth/callback`) |
| `ENVIRONMENT` | `dev` allows the documented bypass when Google ids are unset; never in prod |

Google tokens are **not** stored. The grant is only used to prove identity against the
allowlist (`users` row or `SUPERADMIN_EMAILS`).

## Production note (lnpitask.umn.edu)

Wearable-hub already occupies `/wearable` and host ports around 8000/8010/8020. A later
deploy of this app should follow that Quadlet pattern under a **new** path prefix
(suggest `/qualsched`) and these host ports (8030 backend, 8040 frontend). Do not
put QualSched Web on `/wearable` or on port 8000 (`/qualtrics_dashboard`).

## License

MIT. Same as QualSched desktop. Copyright (c) 2026 Kelvin O. Lim.
