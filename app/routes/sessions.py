from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Session, SessionMaterial, ConnectionRequest, User, create_notification
from app.utils.email_utils import send_email
from app.utils.meetings import new_jitsi_link
from app.utils.storage import save_session_material

sessions_bp = Blueprint("sessions", __name__, url_prefix="/sessions")

VALID_PROVIDERS = {"jitsi", "zoom", "google_meet", "in_person", "other"}


@sessions_bp.route("/schedule/<int:other_user_id>", methods=["GET", "POST"])
@login_required
def schedule(other_user_id):
    other = User.query.get_or_404(other_user_id)

    accepted = ConnectionRequest.query.filter(
        ConnectionRequest.status == "accepted",
        db.or_(
            db.and_(ConnectionRequest.sender_id == current_user.id, ConnectionRequest.receiver_id == other_user_id),
            db.and_(ConnectionRequest.sender_id == other_user_id, ConnectionRequest.receiver_id == current_user.id),
        ),
    ).first()

    if not accepted:
        flash("You need an accepted connection with this user before scheduling a session.", "danger")
        return redirect(url_for("connections.list_requests"))

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        scheduled_at_raw = request.form.get("scheduled_at")
        mentor_id = int(request.form.get("mentor_id"))
        provider = request.form.get("meeting_provider", "jitsi")
        custom_link = request.form.get("meeting_link", "").strip()

        if provider not in VALID_PROVIDERS:
            provider = "jitsi"

        try:
            scheduled_at = datetime.strptime(scheduled_at_raw, "%Y-%m-%dT%H:%M")
        except (ValueError, TypeError):
            flash("Please provide a valid date/time.", "danger")
            return redirect(url_for("sessions.schedule", other_user_id=other_user_id))

        if provider == "jitsi":
            meeting_link = new_jitsi_link()
        elif provider == "in_person":
            meeting_link = ""
        else:
            if not custom_link:
                flash("Please paste your Zoom / Google Meet / other meeting link.", "danger")
                return redirect(url_for("sessions.schedule", other_user_id=other_user_id))
            meeting_link = custom_link

        requester_id = other.id if mentor_id == current_user.id else current_user.id

        new_session = Session(
            requester_id=requester_id,
            mentor_id=mentor_id,
            topic=topic,
            scheduled_at=scheduled_at,
            meeting_provider=provider,
            meeting_link=meeting_link,
        )

        if new_session.has_conflict():
            flash("That mentor already has a session within 60 minutes of this time. Pick another slot.", "danger")
            return redirect(url_for("sessions.schedule", other_user_id=other_user_id))

        db.session.add(new_session)
        db.session.commit()

        create_notification(
            other.id,
            f"{current_user.name} scheduled a session with you: {topic}",
            link=url_for("sessions.list_sessions"),
        )
        send_email(
            other.email,
            "New SkillSwap session scheduled",
            f"{current_user.name} scheduled a session with you on {scheduled_at}.\nTopic: {topic}\n"
            + (f"Join link: {meeting_link}" if meeting_link else "This session is in person."),
        )

        flash("Session scheduled!", "success")
        return redirect(url_for("sessions.list_sessions"))

    return render_template("sessions/form.html", other=other)


@sessions_bp.route("/")
@login_required
def list_sessions():
    my_sessions = Session.query.filter(
        db.or_(Session.requester_id == current_user.id, Session.mentor_id == current_user.id)
    ).order_by(Session.scheduled_at.desc()).all()
    return render_template("sessions/list.html", sessions=my_sessions)


@sessions_bp.route("/<int:session_id>/complete", methods=["POST"])
@login_required
def complete(session_id):
    s = Session.query.get_or_404(session_id)
    if current_user.id not in (s.requester_id, s.mentor_id):
        flash("Not authorized.", "danger")
        return redirect(url_for("sessions.list_sessions"))
    s.status = "completed"
    db.session.commit()
    flash("Session marked as completed. You can now leave a review or add notes/recording.", "success")
    return redirect(url_for("sessions.list_sessions"))


@sessions_bp.route("/<int:session_id>/cancel", methods=["POST"])
@login_required
def cancel(session_id):
    s = Session.query.get_or_404(session_id)
    if current_user.id not in (s.requester_id, s.mentor_id):
        flash("Not authorized.", "danger")
        return redirect(url_for("sessions.list_sessions"))
    s.status = "cancelled"
    db.session.commit()
    flash("Session cancelled.", "info")
    return redirect(url_for("sessions.list_sessions"))


@sessions_bp.route("/<int:session_id>/materials/notes", methods=["POST"])
@login_required
def add_notes(session_id):
    """Upload a PDF/doc of notes. Stays attached to the session forever for both people."""
    s = Session.query.get_or_404(session_id)
    if current_user.id not in (s.requester_id, s.mentor_id):
        flash("Not authorized.", "danger")
        return redirect(url_for("sessions.list_sessions"))

    file = request.files.get("notes_file")
    if not file or not file.filename:
        flash("Please choose a file to upload.", "danger")
        return redirect(url_for("sessions.list_sessions"))

    title = request.form.get("title", "").strip() or file.filename
    url = save_session_material(file)

    db.session.add(SessionMaterial(
        session_id=s.id, uploaded_by_id=current_user.id, kind="notes", title=title, url=url,
    ))
    db.session.commit()

    other = s.other_party(current_user.id)
    create_notification(other.id, f"{current_user.name} added notes to \"{s.topic}\".", link=url_for("sessions.list_sessions"))
    flash("Notes uploaded - they'll stay available on this session for good.", "success")
    return redirect(url_for("sessions.list_sessions"))


@sessions_bp.route("/<int:session_id>/materials/recording", methods=["POST"])
@login_required
def add_recording(session_id):
    """Attach a link to a recorded session (e.g. an unlisted YouTube or Drive link)."""
    s = Session.query.get_or_404(session_id)
    if current_user.id not in (s.requester_id, s.mentor_id):
        flash("Not authorized.", "danger")
        return redirect(url_for("sessions.list_sessions"))

    link = request.form.get("recording_url", "").strip()
    title = request.form.get("title", "").strip() or "Recording"
    if not link:
        flash("Please paste a link to the recording.", "danger")
        return redirect(url_for("sessions.list_sessions"))

    db.session.add(SessionMaterial(
        session_id=s.id, uploaded_by_id=current_user.id, kind="recording", title=title, url=link,
    ))
    db.session.commit()

    other = s.other_party(current_user.id)
    create_notification(other.id, f"{current_user.name} added a recording to \"{s.topic}\".", link=url_for("sessions.list_sessions"))
    flash("Recording link added.", "success")
    return redirect(url_for("sessions.list_sessions"))
