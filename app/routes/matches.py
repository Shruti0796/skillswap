from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.matching import compute_matches

matches_bp = Blueprint("matches", __name__, url_prefix="/matches")


@matches_bp.route("/")
@login_required
def list_matches():
    matches = compute_matches(current_user, limit=25)
    return render_template("matches/list.html", matches=matches)
