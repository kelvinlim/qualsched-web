# lnpitask host runbook (QualSched Web)

Do this **on lnpitask.umn.edu** in Cursor. This agent does not deploy.

Production is Podman Quadlets + host nginx location blocks — not compose.
Same pattern as [wearable-hub](https://github.com/kelvinlim/wearable-hub) `deploy/`
and `scripts/deploy.sh`.

Public URL: **https://lnpitask.umn.edu/qualsched/**

| | QualSched | wearable-hub (do not reuse) |
| --- | --- | --- |
| Path prefix | `/qualsched` only | `/wearable` |
| Host ports | **8030** backend, **8040** frontend | 8010 / 8020 |
| Units | backend + frontend. **No scheduler.** | backend + scheduler + frontend |
| MariaDB | External `cnc3.med.umn.edu`, schema/user `qualsched` | `wearable_hub` |
| MariaDB on lnpitask | None | None |

Do not occupy `/wearable/`, `/enroll`, `/webhooks`, `/qualtrics_dashboard`, or ports 8000 / 8010 / 8020.

PHI stays in Qualtrics. Never commit `.env` or real DB passwords.

## 1. Checkout

```bash
# analogue of /home/kolim/Projects/wearable-hub
cd /home/kolim/Projects
git clone https://github.com/kelvinlim/qualsched-web.git
cd qualsched-web
```

If the tree already exists, `git pull` the commit you want to ship.
Quadlet `EnvironmentFile=` is `/home/kolim/Projects/qualsched-web/.env` — edit the
unit if the checkout path is different.

## 2. `.env`

```bash
cp .env.sample .env
```

Fill in (never commit this file):

| Variable | Production value |
| --- | --- |
| `ENVIRONMENT` | `prod` (disables the local dev-login bypass) |
| `FERNET_KEY` | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `SUPERADMIN_EMAILS` | bootstrap researcher emails, comma-separated |
| `DATABASE_URL` | `mysql+pymysql://qualsched:<password>@cnc3.med.umn.edu:3306/qualsched` |
| `DB_NAME` / `DB_USER` | `qualsched` (not `wearable_hub`) |
| `DB_PASSWORD` | the cnc3 password Kelvin provisions — placeholder in `.env.sample` only |
| `DB_WAIT_HOST` | `cnc3.med.umn.edu` |
| `DB_WAIT_PORT` | `3306` |
| `PUBLIC_PATH_PREFIX` | `/qualsched` |
| `RESEARCHER_OAUTH_REDIRECT_URI` | `https://lnpitask.umn.edu/qualsched/auth/callback` |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | existing Cloud Console web client |

Optional: `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` in `.env` so
`scripts/deploy.sh` can re-export them through `sudo -E podman build`.

## 3. Provision schema/user on cnc3 (Kelvin)

On **cnc3.med.umn.edu**, create a new schema and user named `qualsched`.
Do **not** reuse `wearable_hub` or its credentials. Put the real password only
in the host `.env`.

Example (password is yours; do not commit it):

```sql
CREATE DATABASE qualsched CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'qualsched'@'%' IDENTIFIED BY '...';
GRANT ALL PRIVILEGES ON qualsched.* TO 'qualsched'@'%';
FLUSH PRIVILEGES;
```

Alembic runs from the backend entrypoint on first start (`alembic upgrade head`).
There is no MariaDB container on lnpitask.

## 4. Google redirect URI

In the Google Cloud Console OAuth client (the same web client as local/dev), add:

```
https://lnpitask.umn.edu/qualsched/auth/callback
```

Must match `RESEARCHER_OAUTH_REDIRECT_URI` exactly.

## 5. Install Quadlets

```bash
sudo cp deploy/quadlet/qualsched.network \
        deploy/quadlet/qualsched-backend.container \
        deploy/quadlet/qualsched-frontend.container \
        /etc/containers/systemd/
sudo systemctl daemon-reload
```

Do not copy a scheduler unit — there is none. Do not add a db container.

Images are built by `scripts/deploy.sh` (`localhost/qualsched-backend:latest` and
`localhost/qualsched-frontend:latest`) before the first start.

## 6. Merge host nginx snippet

Copy the `location` blocks from [nginx/qualsched.conf](nginx/qualsched.conf) into
the existing `server { }` that already terminates TLS for `lnpitask.umn.edu`
(typically `/etc/nginx/conf.d/` or a vhost include). Live file is outside the repo.

- Do **not** add a second `server` / `listen` / `ssl` block.
- `location /qualsched/` proxies to `http://127.0.0.1:8040/` and **strips** the
  prefix (trailing URI on `proxy_pass`), same as `/wearable/` → 8020.

```bash
sudo nginx -t && sudo nginx -s reload
```

## 7. Build, start, health-check

```bash
scripts/deploy.sh            # backend + frontend
# scripts/deploy.sh backend  # backend only
# scripts/deploy.sh frontend # frontend only
```

That is `sudo -E podman build` per image, `systemctl restart` of the matching
units, then:

- backend: `curl http://localhost:8030/health`
- frontend: `curl http://localhost:8040/` (container sees `/`, not `/qualsched/`)

Logs: `sudo journalctl -u qualsched-backend.service -f`

Then open https://lnpitask.umn.edu/qualsched/

## Local compose vs this host

`docker-compose.yml` is local-only (sidecar MariaDB `db` on host 3307). It is not
used on lnpitask. Production reads `.env` (cnc3) via the Quadlet `EnvironmentFile`.

## SPA prefix (follow-up, not this PR)

Host nginx strips `/qualsched/` so the frontend container sees `/` — that matches
today's Vite `base: /` and `scripts/deploy.sh` curling `http://localhost:8040/`.
wearable-hub's SPA is built with `base: /wearable/` so the *browser* keeps
assets and API calls under the prefix. If `https://lnpitask.umn.edu/qualsched/`
loads HTML but `/assets/…` or `/api/…` 404 at the site root, set Vite
`base: '/qualsched/'` and prefix frontend `fetch` paths the same way. Do not
change the host nginx strip.
