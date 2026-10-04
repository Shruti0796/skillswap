"""Generates a free, ready-to-use video room link for a session.

Jitsi Meet rooms need no account, no API key, and no setup - a room simply
exists the moment someone opens its URL. This makes it a good default
"hosting" for SkillSwap sessions, with the option for either person to paste
their own Zoom or Google Meet link instead.
"""
import uuid
from flask import current_app


def new_jitsi_link():
    domain = current_app.config.get("JITSI_DOMAIN", "meet.jit.si")
    room = f"skillswap-{uuid.uuid4().hex[:10]}"
    return f"https://{domain}/{room}"
