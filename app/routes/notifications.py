from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required
def list_notifications():
    items = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    for n in items:
        n.is_read = True
    db.session.commit()
    return render_template("notifications/list.html", notifications=items)


@notifications_bp.route("/unread-count")
@login_required
def unread_count():
    # Polled every few seconds by JS to give a lightweight "real-time" bell icon
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"count": count})
