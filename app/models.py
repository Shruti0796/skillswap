from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"<Skill {self.name}>"


class UserSkillTeach(db.Model):
    __tablename__ = "user_skills_teach"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    proficiency = db.Column(db.String(20), default="intermediate")  # beginner/intermediate/expert

    skill = db.relationship("Skill")


class UserSkillLearn(db.Model):
    __tablename__ = "user_skills_learn"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)

    skill = db.relationship("Skill")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, default="")
    profile_pic_url = db.Column(db.String(400), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teach_links = db.relationship("UserSkillTeach", backref="user", cascade="all, delete-orphan")
    learn_links = db.relationship("UserSkillLearn", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def teach_skill_ids(self):
        return {t.skill_id for t in self.teach_links}

    def learn_skill_ids(self):
        return {l.skill_id for l in self.learn_links}

    def teach_proficiency_map(self):
        return {t.skill_id: t.proficiency for t in self.teach_links}

    def average_rating(self):
        reviews = Review.query.filter_by(reviewee_id=self.id).all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 2)

    def review_count(self):
        return Review.query.filter_by(reviewee_id=self.id).count()

    def __repr__(self):
        return f"<User {self.email}>"


class ConnectionRequest(db.Model):
    __tablename__ = "connection_requests"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pending")  # pending/accepted/rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="upcoming")  # upcoming/completed/cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # How this session is held. 'jitsi' links are auto-generated (free, no
    # account needed); 'zoom' / 'google_meet' / 'other' store a link the
    # scheduler pastes in themselves; 'in_person' has no link at all.
    meeting_provider = db.Column(db.String(20), default="jitsi")
    meeting_link = db.Column(db.String(500), default="")

    requester = db.relationship("User", foreign_keys=[requester_id])
    mentor = db.relationship("User", foreign_keys=[mentor_id])
    materials = db.relationship(
        "SessionMaterial", backref="session", cascade="all, delete-orphan",
        order_by="SessionMaterial.created_at.desc()",
    )

    def notes(self):
        return [m for m in self.materials if m.kind == "notes"]

    def recordings(self):
        return [m for m in self.materials if m.kind == "recording"]

    def other_party(self, current_user_id):
        return self.mentor if current_user_id == self.requester_id else self.requester

    def has_conflict(self):
        """Check whether the mentor already has a session within 60 minutes of this one."""
        from datetime import timedelta
        window_start = self.scheduled_at - timedelta(minutes=60)
        window_end = self.scheduled_at + timedelta(minutes=60)
        q = Session.query.filter(
            Session.mentor_id == self.mentor_id,
            Session.status == "upcoming",
            Session.scheduled_at.between(window_start, window_end),
        )
        if self.id:
            q = q.filter(Session.id != self.id)
        return q.first() is not None


class SessionMaterial(db.Model):
    """Notes/PDFs or recording links attached to a session, kept forever
    so both people can come back to them long after the session ends."""
    __tablename__ = "session_materials"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    kind = db.Column(db.String(20), nullable=False)  # 'notes' or 'recording'
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploaded_by = db.relationship("User")


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("Session")


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(300), default="")
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def create_notification(user_id, message, link=""):
    n = Notification(user_id=user_id, message=message, link=link)
    db.session.add(n)
    db.session.commit()
    return n
