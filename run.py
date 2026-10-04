import os
from app import create_app, db
from app.models import User, Skill

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Create all tables. Usage: flask --app run.py init-db"""
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
