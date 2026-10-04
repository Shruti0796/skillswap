import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Defaults to local SQLite so the app runs with zero setup.
    # For Neon (or any managed Postgres), set DATABASE_URL to something like:
    #   postgresql://user:password@ep-your-project.us-east-2.aws.neon.tech/skillswap?sslmode=require
    # Neon requires sslmode=require - make sure it's in the connection string.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'skillswap.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # avoids stale-connection errors with Neon's autosuspend

    S3_BUCKET = os.environ.get("S3_BUCKET", "").strip()
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    SES_SENDER_EMAIL = os.environ.get("SES_SENDER_EMAIL", "").strip()

    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB upload limit

    # Matching engine weights (tune these to change how matches are ranked)
    WEIGHT_DIRECT_MATCH = 0.5      # how much of what YOU want to learn, they can teach
    WEIGHT_RECIPROCAL_MATCH = 0.3  # how much of what YOU can teach, they want to learn
    WEIGHT_RATING = 0.2            # their average rating from past sessions

    PROFICIENCY_WEIGHTS = {"beginner": 0.4, "intermediate": 0.7, "expert": 1.0}

    # Video hosting for sessions. Jitsi Meet (meet.jit.si) is a free public
    # video service - no account or API key needed, rooms are created just by
    # visiting a URL. Point this at a self-hosted Jitsi instance on AWS later
    # if you want full control (see README).
    JITSI_DOMAIN = os.environ.get("JITSI_DOMAIN", "meet.jit.si")
