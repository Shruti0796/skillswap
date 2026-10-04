from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        from app.matching import compute_matches
        top_matches = compute_matches(current_user, limit=3)
        return render_template("index.html", top_matches=top_matches)
    return render_template("index.html", top_matches=None)
