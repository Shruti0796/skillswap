from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Skill, UserSkillTeach, UserSkillLearn, User
from app.utils.storage import save_profile_picture

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    all_skills = Skill.query.order_by(Skill.name).all()

    if request.method == "POST":
        current_user.bio = request.form.get("bio", "").strip()

        picture = request.files.get("profile_pic")
        if picture and picture.filename:
            current_user.profile_pic_url = save_profile_picture(picture)

        # --- Skills I can teach (with proficiency) ---
        UserSkillTeach.query.filter_by(user_id=current_user.id).delete()
        teach_skill_ids = request.form.getlist("teach_skill_ids")
        for sid in teach_skill_ids:
            proficiency = request.form.get(f"proficiency_{sid}", "intermediate")
            db.session.add(UserSkillTeach(user_id=current_user.id, skill_id=int(sid), proficiency=proficiency))

        # --- Skills I want to learn ---
        UserSkillLearn.query.filter_by(user_id=current_user.id).delete()
        learn_skill_ids = request.form.getlist("learn_skill_ids")
        for sid in learn_skill_ids:
            db.session.add(UserSkillLearn(user_id=current_user.id, skill_id=int(sid)))

        # --- New custom skill, if the user typed one that doesn't exist yet ---
        new_skill_name = request.form.get("new_skill_name", "").strip()
        if new_skill_name:
            existing = Skill.query.filter(Skill.name.ilike(new_skill_name)).first()
            if not existing:
                existing = Skill(name=new_skill_name)
                db.session.add(existing)
                db.session.flush()
            role = request.form.get("new_skill_role")
            if role == "teach":
                db.session.add(UserSkillTeach(user_id=current_user.id, skill_id=existing.id, proficiency="intermediate"))
            elif role == "learn":
                db.session.add(UserSkillLearn(user_id=current_user.id, skill_id=existing.id))

        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("profile.view", user_id=current_user.id))

    my_teach_ids = current_user.teach_skill_ids()
    my_learn_ids = current_user.learn_skill_ids()
    proficiency_map = current_user.teach_proficiency_map()

    return render_template(
        "profile/edit.html",
        all_skills=all_skills,
        my_teach_ids=my_teach_ids,
        my_learn_ids=my_learn_ids,
        proficiency_map=proficiency_map,
    )


@profile_bp.route("/<int:user_id>")
@login_required
def view(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("profile/view.html", user=user)
