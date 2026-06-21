from django.core.mail import send_mail
from django.conf import settings


def send_security_alert(sender_email, attempts):
    subject = "Security Alert: Unauthorized Decode Attempts Detected"

    body = f"""
Someone attempted multiple incorrect secret keys on your encoded image.

Attempts: {attempts}

Possible brute-force activity detected.

Your encoded message remains protected.

Login to your account and use your image key to manage this encoded image.
"""

    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [sender_email],
        fail_silently=False,
    )





def send_verification_email(user_email, verification_link):
    subject = "Activate Your Steganography Hub Account"

    body = f"""
Hello,

Thank you for creating an account.

Please activate your account using the link below:

{verification_link}

If you did not request this, you can safely ignore this email.
"""

    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )