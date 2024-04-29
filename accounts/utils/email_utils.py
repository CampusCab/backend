import resend
from random import choices
from string import ascii_uppercase, digits
from django.conf import settings

def send_email(user, code):

    resend.api_key = settings.RESEND_API_KEY

    params = {
        "from": "CampusCab",
        "to": user.email,
        "subject": f"CampusCab 🚖 - Tu código de verificación es: {code}",
    }

    try:
        resend.Emails.send(params)
        return True
    except Exception:
        return False


def generate_code():
    chars = ascii_uppercase + digits
    return "".join(choices(chars, k=6))
