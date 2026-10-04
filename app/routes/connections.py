from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import ConnectionRequest, User, create_notification

connections_bp = Blueprint("connections", __name__, url_prefix="/connections")


@connections_bp.route("/send/<int:receiver_id>", methods=["POST"])
@login_required
def send_request(receiver_id):
    if receiver_id == current_user.id:
        flash("You can't send a request to yourself.", "danger")
        return redirect(url_for("matches.list_matches"))

    existing = ConnectionRequest.query.filter_by(
        sender_id=current_user.id, receiver_id=receiver_id, status="pending"
    ).first()
    if existing:
        flash("You already have a pending request with this user.", "info")
        return redirect(url_for("matches.list_matches"))

    message = request.form.get("message", "").strip()
    req = ConnectionRequest(sender_id=current_user.id, receiver_id=receiver_id, message=message)
    db.session.add(req)
    db.session.commit()

    create_notification(
        receiver_id,
        f"{current_user.name} sent you a connection request.",
        link=url_for("connections.list_requests"),
    )
    flash("Request sent!", "success")
    return redirect(url_for("matches.list_matches"))


@connections_bp.route("/")
@login_required
def list_requests():
    received = ConnectionRequest.query.filter_by(receiver_id=current_user.id).order_by(
        ConnectionRequest.created_at.desc()
    ).all()
    sent = ConnectionRequest.query.filter_by(sender_id=current_user.id).order_by(
        ConnectionRequest.created_at.desc()
    ).all()
    return render_template("connections/list.html", received=received, sent=sent)


@connections_bp.route("/<int:request_id>/respond", methods=["POST"])
@login_required
def respond(request_id):
    req = ConnectionRequest.query.get_or_404(request_id)
    if req.receiver_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("connections.list_requests"))

    action = request.form.get("action")
    if action == "accept":
        req.status = "accepted"
        create_notification(
            req.sender_id,
            f"{current_user.name} accepted your connection request!",
            link=url_for("connections.list_requests"),
        )
        flash("Request accepted.", "success")
    elif action == "reject":
        req.status = "rejected"
        flash("Request rejected.", "info")

    db.session.commit()
    return redirect(url_for("connections.list_requests"))
