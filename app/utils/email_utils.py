import os
import resend


resend.api_key = os.environ.get("RESEND_API_KEY")


def send_email(to, subject, html):
    params = {
        "from": os.environ.get(
            "RESEND_FROM_EMAIL",
            "onboarding@resend.dev"
        ),
        "to": [to],
        "subject": subject,
        "html": html,
    }

    return resend.Emails.send(params)
