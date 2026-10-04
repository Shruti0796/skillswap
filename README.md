# SkillSwap – Peer-to-Peer Skill Exchange & Mentorship Platform

A Flask app with:

- User registration/login with password confirmation and a show/hide toggle on every password field
- Profiles with skills you can teach (with proficiency level) and skills you want to learn
- **Smarter matching engine** — scores every other user (not just perfect mutual matches) based on direct relevance, reciprocity, and reputation
- Connection requests (send/accept/reject)
- **Session scheduling with real video hosting** — every session auto-generates a free Jitsi Meet video room (no account needed), or you can paste your own Zoom / Google Meet link, or mark it in-person
- **Session notes & recordings that stay forever** — upload a PDF/doc of notes or paste a recording link, attached permanently to the session for both people to revisit any time
- Ratings & reviews (only allowed after a session is marked completed)
- In-app notification bell that polls every 10s
- A proper **app shell UI** — fixed sidebar navigation, not a marketing page — built as a from-scratch design system (no Bootstrap, no template kit)

Runs locally on SQLite with zero setup, and is wired for **Neon Postgres** + **AWS** in production via environment variables only — no code changes.

---

## 1. Run it locally

```bash
cd skillswap
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python seed.py                  # starter skills + 2 demo users
python run.py
```

Open **http://localhost:5000**. Demo logins: `alice@example.com` / `bob@example.com`, password `password123`.

> If you're upgrading from an earlier version of this project, delete the old `skillswap.db` and re-run `python seed.py` — the database schema changed (new session/materials columns).

### Try the video + notes flow
1. Log in as Alice, accept/send a request with Bob, then **Schedule session**.
2. Leave "How will you meet?" on the default option — this generates a real, joinable Jitsi Meet link automatically.
3. On the Sessions page, click **Join session** to open it.
4. Open the **Notes & recording** panel on that session card, upload a PDF, or paste a link to a recording. It's saved permanently — log in as Bob and you'll see it too.

---

## 2. Password handling

- Registration requires the password twice (`password` + `confirm_password`) and rejects the submission server-side if they don't match, or if the password is under 8 characters.
- Every password field has a show/hide eye icon (`app/static/js/password-toggle.js`) so people can check what they typed before submitting — this is a client-side convenience only; the actual password is still sent over HTTPS and stored as a salted hash (`werkzeug.security.generate_password_hash`), never in plain text.

---

## 3. Video hosting: how it works without any API keys

Sessions use **Jitsi Meet** (`meet.jit.si`) by default — a public, free video service where a room exists the instant someone opens its URL. `app/utils/meetings.py` just builds a URL like `https://meet.jit.si/skillswap-<random-id>`; there's no signup, API key, or webhook to configure. People can also paste their own Zoom or Google Meet link instead, or mark a session as in-person.

If you outgrow the public Jitsi service (e.g. you want branding or higher participant limits), you can self-host Jitsi on its own AWS EC2 instance and just change `JITSI_DOMAIN` in your environment — no other code changes needed.

---

## 4. Project structure

```
skillswap/
  run.py / seed.py / requirements.txt / .env.example
  app/
    config.py            # env-driven config (DB, S3, SES, Jitsi, matching weights)
    models.py             # SQLAlchemy models, incl. Session + SessionMaterial
    matching.py            # the scoring/matching engine
    routes/                 # one blueprint per feature area
    utils/
      storage.py             # profile pics + session materials, S3 or local
      email_utils.py          # SES or console fallback
      meetings.py              # Jitsi link generator
    templates/
      base_public.html         # logged-out shell (landing, login, register)
      base_app.html              # logged-in app shell (sidebar navigation)
      ...
    static/
      css/style.css              # the whole design system, no framework
      js/notifications.js         # notification bell polling
      js/password-toggle.js        # show/hide password
```

---

## 5. Moving to production: Neon + AWS

### Database — Neon (serverless Postgres)
1. Create a free project at neon.tech, and copy its connection string.
2. Add `psycopg2-binary` is already in `requirements.txt`.
3. Set in your environment:
   ```
   DATABASE_URL=postgresql://<user>:<password>@<your-project>.neon.tech/skillswap?sslmode=require
   ```
   Neon **requires** `sslmode=require` — don't drop it from the URL.
4. Neon auto-suspends idle databases and wakes on the next query; `SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}` (already set in `config.py`) prevents stale-connection errors when that happens.
5. Create the tables once against Neon: `flask --app run.py init-db` (or `python seed.py` to also add starter data).

### Hosting — AWS Elastic Beanstalk
```bash
pip install awsebcli
eb init -p python-3.11 skillswap
eb create skillswap-env
eb setenv SECRET_KEY=... DATABASE_URL=... S3_BUCKET=... AWS_REGION=... SES_SENDER_EMAIL=...
eb deploy
```
Attach an IAM role to the EB environment with least-privilege access to your S3 bucket — don't use hardcoded access keys in production.

### File storage — S3 (profile pictures + session notes/PDFs)
Set `S3_BUCKET` and `AWS_REGION`; uploads switch from local disk to S3 automatically — no code changes.

### Email — SES
Set `SES_SENDER_EMAIL` once verified in SES; console-logging emails switch to real sends automatically.

### Video — Jitsi (see section 3 above)
The public `meet.jit.si` works out of the box. Self-hosting is optional and only worth it at scale.

---

## 6. Notes on the design

The old version used Bootstrap and a marketing-page layout. This version is a real app shell: a persistent sidebar (Dashboard / Matches / Requests / Sessions / Notifications / Profile), a single typeface (Manrope) at multiple weights, and a muted slate-blue accent instead of bright colors — built entirely in `app/static/css/style.css` with no CSS framework, so every visual choice is easy to trace and change.
