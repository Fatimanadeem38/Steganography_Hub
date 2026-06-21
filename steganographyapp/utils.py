import base64
import hashlib
import secrets
import string

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse


def generate_key(length=16):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_image_id():
    return "IMG-" + generate_key(8).upper()


def generate_unfreeze_token():
    return secrets.token_urlsafe(48)


def hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()


def verify_key(input_key, stored_hash):
    return hash_key(input_key) == stored_hash


def get_fernet():
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


def encrypt_key_value(value):
    fernet = get_fernet()
    return fernet.encrypt(value.encode()).decode()


def decrypt_key_value(value):
    fernet = get_fernet()
    return fernet.decrypt(value.encode()).decode()


def build_absolute_url(request, url_name, **kwargs):
    relative_url = reverse(url_name, kwargs=kwargs)
    return request.build_absolute_uri(relative_url)


def send_receiver_credentials_email(
    receiver_email,
    sender_username,
    image_id,
    secret_key,
    encoded_image_path=None
):
    if not receiver_email:
        return False

    subject = "Your Steganography Decoding Credentials"

    text_content = f"""
Hello,

You have received an encoded image from {sender_username}.

Use the following credentials to decode the hidden message:

Image ID: {image_id}
Secret Key: {secret_key}

Please keep these details private.

Important:
The Image Key is not shared with you because it is only used by the sender to manage the encoded image.

Regards,
Steganography Hub
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2 style="color:#5b21b6;">Steganography Hub</h2>

        <p>Hello,</p>

        <p>You have received an encoded image from <strong>{sender_username}</strong>.</p>

        <p>Use the following credentials to decode the hidden message:</p>

        <div style="background:#f4f4f4; padding:15px; border-radius:8px;">
            <p><strong>Image ID:</strong> {image_id}</p>
            <p><strong>Secret Key:</strong> {secret_key}</p>
        </div>

        <p>Please keep these details private.</p>

        <p>
            <strong>Important:</strong> The Image Key is not shared with you because it is only used by the sender
            to manage the encoded image.
        </p>

        <p>Regards,<br>Steganography Hub</p>
    </div>
    """

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[receiver_email],
        )

        email.attach_alternative(html_content, "text/html")

        if encoded_image_path:
            try:
                email.attach_file(encoded_image_path)
            except Exception:
                pass

        email.send(fail_silently=False)
        return True

    except Exception:
        return False


def send_security_warning_email(
    sender_email,
    sender_username,
    image_id,
    failed_attempts
):
    if not sender_email:
        return False

    subject = "Security Warning: Wrong Decode Attempts Detected"

    text_content = f"""
Hello {sender_username},

Security warning for your encoded image.

Image ID: {image_id}
Wrong Decode Attempts: {failed_attempts}

The receiver has entered the wrong Secret Key multiple times.
For security, decoding has been temporarily blocked for 2 minutes.

Regards,
Steganography Hub
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2 style="color:#b45309;">Security Warning</h2>

        <p>Hello <strong>{sender_username}</strong>,</p>

        <p>Wrong decode attempts were detected for your encoded image.</p>

        <div style="background:#fff7ed; padding:15px; border-radius:8px; border-left:4px solid #f59e0b;">
            <p><strong>Image ID:</strong> {image_id}</p>
            <p><strong>Wrong Decode Attempts:</strong> {failed_attempts}</p>
        </div>

        <p>
            The receiver has entered the wrong Secret Key multiple times.
            Decoding has been temporarily blocked for 2 minutes.
        </p>

        <p>Regards,<br>Steganography Hub</p>
    </div>
    """

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sender_email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        return True

    except Exception:
        return False


def send_unfreeze_confirmation_email(
    sender_email,
    sender_username,
    image_id,
    unfreeze_url
):
    if not sender_email:
        return False

    subject = "Action Required: Confirm Image Unfreeze"

    text_content = f"""
Hello {sender_username},

Your encoded image has been frozen because 5 wrong decode attempts were detected.

Image ID: {image_id}

If this activity is trusted, you can unfreeze the image using the link below:

{unfreeze_url}

If you do not recognize this activity, ignore this email and keep the image frozen.

Regards,
Steganography Hub
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #222;">
        <h2 style="color:#dc2626;">Image Frozen</h2>

        <p>Hello <strong>{sender_username}</strong>,</p>

        <p>
            Your encoded image has been frozen because
            <strong>5 wrong decode attempts</strong> were detected.
        </p>

        <div style="background:#fef2f2; padding:15px; border-radius:8px; border-left:4px solid #dc2626;">
            <p><strong>Image ID:</strong> {image_id}</p>
        </div>

        <p>
            If this activity is trusted, click the button below to unfreeze the image.
        </p>

        <p style="margin:25px 0;">
            <a href="{unfreeze_url}"
               style="background:#5b21b6; color:#ffffff; padding:12px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">
                Confirm Unfreeze
            </a>
        </p>

        <p>
            If you do not recognize this activity, ignore this email and keep the image frozen.
        </p>

        <p>Regards,<br>Steganography Hub</p>
    </div>
    """

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sender_email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        return True

    except Exception:
        return False