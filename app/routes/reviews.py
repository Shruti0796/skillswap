from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Session, Review, create_notification

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@reviews_bp.route("/session/<int:session_id>", methods=["GET", "POST"])
@login_required
def add_review(session_id):
    s = Session.query.get_or_404(session_id)

    if current_user.id not in (s.requester_id, s.mentor_id):
        flash("Not authorized.", "danger")
        return redirect(url_for("sessions.list_sessions"))

    if s.status != "completed":
        flash("You can only review a session after it's marked completed.", "danger")
        return redirect(url_for("sessions.list_sessions"))

    reviewee = s.other_party(current_user.id)

    existing = Review.query.filter_by(session_id=s.id, reviewer_id=current_user.id).first()
    if existing:
        flash("You've already reviewed this session.", "info")
        return redirect(url_for("sessions.list_sessions"))

    if request.method == "POST":
        rating = int(request.form.get("rating", 5))
        comment = request.form.get("comment", "").strip()

        review = Review(
            session_id=s.id,
            reviewer_id=current_user.id,
            reviewee_id=reviewee.id,
            rating=max(1, min(5, rating)),
            comment=comment,
        )
        db.session.add(review)
        db.session.commit()

        create_notification(
            reviewee.id,
            f"{current_user.name} left you a {review.rating}-star review.",
            link=url_for("profile.view", user_id=reviewee.id),
        )
        flash("Review submitted. Thanks for helping keep SkillSwap trustworthy!", "success")
        return redirect(url_for("sessions.list_sessions"))

    return render_template("reviews/form.html", session=s, reviewee=reviewee)
