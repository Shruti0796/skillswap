# SkillSwap

### [INTRACTIVE README — Try SkillSwap Here](https://shruti0796.github.io/skillswap/)

**Teach what you know. Learn what you don’t.**
A peer-to-peer skill exchange and mentorship platform built with Flask and deployed on free-tier cloud services.

## Features

- **Smart matching:** every user gets a 0–100% score from skill overlap, reciprocity and ratings, so partial matches show up too.
- **Profiles:** skills to teach (beginner / intermediate / expert), skills to learn, bio and photo.
- **Connections:** send, accept or decline requests.
- **Sessions:** auto-generated Jitsi video room, or a pasted Zoom / Google Meet link, or in person. Mentors can’t be double booked within 60 minutes.
- **Permanent notes:** upload PDFs/docs or attach recording links to a session; both people keep them.
- **Reviews:** 1–5 stars, only after a session is completed, once per person.
- **Notifications:** in-app bell (polls every 10 s) plus email on new sessions.
- **Responsive UI:** desktop, tablet and phone.

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python 3, Flask 3, Flask-SQLAlchemy, Flask-Login, Gunicorn |
| Frontend | Jinja2, HTML5, CSS3, vanilla JavaScript (no framework) |
| Hosting | Render |
| Database | Neon (PostgreSQL); SQLite locally |
| File storage | Supabase Storage |
| Email | Resend |
| Video | Jitsi Meet |

## Architecture

```
Browser ──HTTPS──▶ Render (Gunicorn + Flask)
                     ├──▶ Neon             PostgreSQL (SQLAlchemy / TLS)
                     ├──▶ Supabase Storage profile pictures, session notes
                     ├──▶ Resend           notification emails
                     └──▶ Jitsi Meet       generates a room link per session
```

## Quick start (local)

No cloud accounts needed: it falls back to SQLite, local file storage and console-printed emails.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # optional
python seed.py                  # creates tables, starter skills, demo users
python run.py                   # http://localhost:5000
```

Demo logins: `alice@example.com` / `bob@example.com`, password `password123`.

## Configuration

Set these as environment variables (or in `.env` locally).

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Signs login sessions |
| `DATABASE_URL` | Neon connection string, must include `sslmode=require` |
| `SUPABASE_URL` | `https://<project>.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side storage key. Never expose it. |
| `SUPABASE_BUCKET` | Public bucket name |
| `RESEND_API_KEY` | Resend API key |
| `RESEND_FROM_EMAIL` | Sender on a verified domain |
| `JITSI_DOMAIN` | Optional, defaults to `meet.jit.si` |

## Deploy

1. Push the repo to GitHub.
2. **Neon:** create a project and copy the connection string.
3. **Supabase:** create a project, add a **public** Storage bucket, copy the URL and service-role key.
4. **Resend:** create an API key.
5. **Render:** new Web Service from the repo. Build: `pip install -r requirements.txt`. Start: `gunicorn run:app`.
6. Add the environment variables above in Render.
7. Run `python seed.py` once with `DATABASE_URL` pointing at Neon to create the tables.

## Matching engine

```
score = 0.5 × direct + 0.3 × reciprocal + 0.2 × reputation
```

- **direct:** how much of what you want to learn they can teach, weighted by their level (beginner 0.4, intermediate 0.7, expert 1.0).
- **reciprocal:** how much of what you teach they want to learn.
- **reputation:** average rating ÷ 5 (0.6 for users with no reviews yet).

## Project structure

```
run.py  seed.py  requirements.txt  .env.example
app/
  config.py  models.py  matching.py
  routes/   auth, profile, matches, connections, sessions, reviews, notifications
  utils/    storage.py, email_utils.py, meetings.py
  templates/  base_public.html, base_app.html, ...
  static/     css/style.css, js/
```

## Known limitations

- Resend only emails the account owner until a domain is verified; in-app notifications reach everyone.
- Public Jitsi rooms may show “waiting for moderator”. Use a Zoom/Meet link or self-host Jitsi.
- No CSRF tokens, email verification or password reset yet.
- Render’s free plan sleeps when idle, so the first request can be slow.

## Roadmap

WebSocket notifications and chat, calendar invites, admin panel, signed URLs for private files, automated tests.

The old version used Bootstrap and a marketing-page layout. This version is a real app shell: a persistent sidebar (Dashboard / Matches / Requests / Sessions / Notifications / Profile), a single typeface (Manrope) at multiple weights, and a muted slate-blue accent instead of bright colors — built entirely in `app/static/css/style.css` with no CSS framework, so every visual choice is easy to trace and change.
