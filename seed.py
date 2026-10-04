"""Seed the database with a starter list of skills and a couple of demo users.
Run with: python seed.py
"""
from app import create_app, db
from app.models import Skill, User, UserSkillTeach, UserSkillLearn

app = create_app()

STARTER_SKILLS = [
    "Python", "JavaScript", "UI/UX Design", "Public Speaking", "Excel",
    "Guitar", "Photography", "Creative Writing", "Data Analysis", "Spanish",
    "Video Editing", "Digital Marketing",
]

with app.app_context():
    db.create_all()

    for name in STARTER_SKILLS:
        if not Skill.query.filter_by(name=name).first():
            db.session.add(Skill(name=name))
    db.session.commit()

    if not User.query.filter_by(email="alice@example.com").first():
        alice = User(name="Alice", email="alice@example.com", bio="I love teaching Python!")
        alice.set_password("password123")
        db.session.add(alice)
        db.session.commit()

        python_skill = Skill.query.filter_by(name="Python").first()
        uiux_skill = Skill.query.filter_by(name="UI/UX Design").first()
        db.session.add(UserSkillTeach(user_id=alice.id, skill_id=python_skill.id, proficiency="expert"))
        db.session.add(UserSkillLearn(user_id=alice.id, skill_id=uiux_skill.id))

    if not User.query.filter_by(email="bob@example.com").first():
        bob = User(name="Bob", email="bob@example.com", bio="UI/UX designer looking to learn to code.")
        bob.set_password("password123")
        db.session.add(bob)
        db.session.commit()

        python_skill = Skill.query.filter_by(name="Python").first()
        uiux_skill = Skill.query.filter_by(name="UI/UX Design").first()
        db.session.add(UserSkillTeach(user_id=bob.id, skill_id=uiux_skill.id, proficiency="expert"))
        db.session.add(UserSkillLearn(user_id=bob.id, skill_id=python_skill.id))

    db.session.commit()
    print("Seed complete. Demo logins: alice@example.com / bob@example.com, password: password123")
