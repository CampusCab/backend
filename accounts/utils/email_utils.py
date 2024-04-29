import resend
from random import choices
from string import ascii_uppercase, digits
from django.conf import settings

def send_email(user, code):
    sender = settings.RESEND_DOMAIN
    receiver = user.email

    params = {
        "from": f"CampusCab <{sender}>",
        "to": [receiver],
        "subject": f"🚖 CampusCab - Tu código de verificación es {code}",
        "html": f"""
            <h2>{user.first_name}, este es tu código de verificación 🔑</h2>
            <p>Ingresa el siguiente código en la aplicación para verificar tu cuenta: <b>{code}</b></p>
            <h5><i>No compartas este código con nadie. Si no solicitaste este código, ignora este mensaje.</i></h5>
        """
    }

    try:
        resend.Emails.send(params)
        return True
    except Exception as e:
        return False


def generate_code():
    chars = ascii_uppercase + digits
    return "".join(choices(chars, k=6))
