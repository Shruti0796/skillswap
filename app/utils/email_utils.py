
import os
import resend
from flask import current_app

resend.api_key = os.environ.get("RESEND_API_KEY")


def send_email(to, subject, html):
    params = {
        "from": os.environ.get(
            "RESEND_FROM_EMAIL",
            "onboarding@resend.dev",
        ),
        "to": [to],
        "subject": subject,
        "html": html,
    }

    try:
        result = resend.Emails.send(params)
        current_app.logger.info("Email request accepted by Resend.")
        return result

    except Exception:
        current_app.logger.exception(
            "Email failed; continuing without notification."
        )
        return None
