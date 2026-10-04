"""
Transactional email sending.
- If SES_SENDER_EMAIL is set, sends via Amazon SES.
- Otherwise, just logs the email to the console (handy for local dev/testing
  without any AWS setup at all).
"""
from flask import current_app


def send_email(to_address, subject, body_text):
    sender = current_app.config.get("SES_SENDER_EMAIL")

    if not sender:
        print(f"\n----- [DEV EMAIL] -----\nTo: {to_address}\nSubject: {subject}\n\n{body_text}\n------------------------\n")
        return

    import boto3
    client = boto3.client("ses", region_name=current_app.config["AWS_REGION"])
    client.send_email(
        Source=sender,
        Destination={"ToAddresses": [to_address]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body_text}},
        },
    )
