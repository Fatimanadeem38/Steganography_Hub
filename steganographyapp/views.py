import os
import uuid
from datetime import timedelta
from django.core.mail import send_mail
from django.http import HttpResponse
import cv2
import numpy as np
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import SignupForm, LoginForm
from .models import EncodedMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from .email_utils import send_verification_email
from .stego_utils import (
    encrypt_message,
    decrypt_message,
    encode_fusion_stego,
    decode_fusion_stego,
    calculate_mse,
    calculate_psnr,
    calculate_ssim,
)
from .utils import (
    generate_key,
    generate_image_id,
    generate_unfreeze_token,
    hash_key,
    verify_key,
    encrypt_key_value,
    decrypt_key_value,
    build_absolute_url,
    send_receiver_credentials_email,
    send_security_warning_email,
    send_unfreeze_confirmation_email,
)

def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")

def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        login(request, user)
        messages.success(request, "Your account has been activated successfully.")
        return redirect("home")

    messages.error(request, "Verification link is invalid or expired.")
    return redirect("signup")


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            if User.objects.filter(email=email).exists():
                messages.error(request, "This email address is already registered.")
                return redirect("signup")

            user = form.save(commit=False)
            user.email = email
            user.set_password(form.cleaned_data["password"])

            # keep active while generating token
            user.is_active = True
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # now block login until email verification
            user.is_active = False
            user.save()

            verification_link = request.build_absolute_uri(
                reverse("verify_email", kwargs={"uidb64": uid, "token": token})
            )

            try:
                send_verification_email(user.email, verification_link)
                return redirect("activation_sent")

            except Exception as e:
                user.delete()
                messages.error(request, f"Confirmation email could not be sent: {e}")
                return redirect("signup")

        messages.error(request, "Please check your signup details.")

    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})

def activation_sent_view(request):
    return render(request, "activation_sent.html")

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        user_obj = User.objects.filter(email=username_or_email).first()
        username = user_obj.username if user_obj else username_or_email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Please activate your account through email before login.")
                return redirect("login")

            login(request, user)
            messages.success(request, "Login successful.")
            return redirect("home")   # changed from encode to home

        else:
            messages.error(request, "Invalid username/email or password.")
            return redirect("login")

    form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")

@login_required
def encode_view(request):
    anime_dir = os.path.join(settings.MEDIA_ROOT, "anime_dataset")
    anime_images = []

    if os.path.exists(anime_dir):
        for img in os.listdir(anime_dir):

            if img.lower().endswith((".png", ".jpg", ".jpeg")):

                img_path = os.path.join(anime_dir, img)

                try:
                    image = cv2.imread(img_path, 0)

                    if image is None:
                        continue

                    edges = cv2.Canny(image, 100, 200)
                    edge_pixels = np.sum(edges > 0)
                    approx_capacity = edge_pixels // 8

                    if approx_capacity >= 1000:
                        anime_images.append(img)

                except Exception:
                    pass

    user_images = EncodedMessage.objects.filter(
        sender=request.user
    ).order_by("-created_at")

    if request.method == "POST":

        secret_message = request.POST.get("secret_message")
        receiver_email = request.POST.get("receiver_email")
        selected_image = request.POST.get("selected_image")
        send_email_to_receiver = request.POST.get("send_email_to_receiver")

        if not secret_message or not selected_image:
            messages.error(
                request,
                "Please enter message and select an anime image."
            )
            return redirect("encode")

        original_path = os.path.join(anime_dir, selected_image)

        if not os.path.exists(original_path):
            messages.error(request, "Selected image not found.")
            return redirect("encode")

        encrypted_message = encrypt_message(secret_message)

        image_id = generate_image_id()

        while EncodedMessage.objects.filter(image_id=image_id).exists():
            image_id = generate_image_id()

        secret_key = generate_key(16)
        image_key = generate_key(16)

        encoded_filename = f"encoded_{uuid.uuid4().hex}.png"

        encoded_folder = os.path.join(
            settings.MEDIA_ROOT,
            "encoded_images"
        )

        os.makedirs(encoded_folder, exist_ok=True)

        encoded_path = os.path.join(
            encoded_folder,
            encoded_filename
        )

        try:
            encode_fusion_stego(
                image_path=original_path,
                encrypted_message=encrypted_message,
                output_path=encoded_path,
                secret_key=secret_key
            )

            mse = calculate_mse(original_path, encoded_path)
            psnr = calculate_psnr(mse)
            ssim_value = calculate_ssim(original_path, encoded_path)

            encoded_obj = EncodedMessage.objects.create(
                sender=request.user,

                image_id=image_id,

                original_image_name=selected_image,

                encoded_image=f"encoded_images/{encoded_filename}",

                secret_key_hash=hash_key(secret_key),
                image_key_hash=hash_key(image_key),

                secret_key_encrypted=encrypt_key_value(secret_key),
                image_key_encrypted=encrypt_key_value(image_key),

                encrypted_message=encrypted_message,

                receiver_email=receiver_email,

                mse_value=mse,
                psnr_value=psnr,
                ssim_value=ssim_value,
            )

            email_sent = False

            if receiver_email and send_email_to_receiver == "on":

                email_sent = send_receiver_credentials_email(
                    receiver_email=receiver_email,
                    sender_username=request.user.username,
                    image_id=image_id,
                    secret_key=secret_key,
                    encoded_image_path=encoded_path
                )

            request.session["last_encoded"] = {
                "encoded_id": encoded_obj.id,
                "image_id": image_id,
                "secret_key": secret_key,
                "image_key": image_key,
                "email_sent": email_sent,
            }

            return redirect("encode")

        except ValueError as e:

            if "Message is too large" in str(e):

                messages.error(
                    request,
                    "Your message is too large for the selected image. Please select a larger image or use a shorter message."
                )

            else:
                messages.error(request, str(e))

            return redirect("encode")

        except Exception as e:
            messages.error(request, f"Encoding failed: {e}")
            return redirect("encode")

    last_encoded = request.session.pop("last_encoded", None)

    recovered_credentials = request.session.pop(
        "recovered_credentials",
        None
    )

    context = {
        "anime_images": anime_images,
        "user_images": user_images,
    }

    if last_encoded:

        try:
            encoded_obj = EncodedMessage.objects.get(
                id=last_encoded["encoded_id"],
                sender=request.user
            )

            context.update({
                "success": True,
                "encoded_obj": encoded_obj,

                "image_id": last_encoded["image_id"],
                "secret_key": last_encoded["secret_key"],
                "image_key": last_encoded["image_key"],

                "email_sent": last_encoded["email_sent"],
            })

        except EncodedMessage.DoesNotExist:
            pass

    if recovered_credentials:

        context.update({
            "recovered_credentials": recovered_credentials
        })

    return render(request, "encode.html", context)
@login_required
def unfreeze_image_view(request, token):
    try:
        encoded_obj = EncodedMessage.objects.get(
            unfreeze_token=token,
            sender=request.user
        )

    except EncodedMessage.DoesNotExist:
        messages.error(request, "Invalid or expired unfreeze link.")
        return redirect("encode")

    if encoded_obj.unfreeze_token_created_at:
        token_age = timezone.now() - encoded_obj.unfreeze_token_created_at

        if token_age > timedelta(hours=24):
            messages.error(request, "This unfreeze link has expired.")
            return redirect("encode")

    encoded_obj.failed_attempts = 0
    encoded_obj.temporary_locked_until = None
    encoded_obj.is_permanently_locked = False
    encoded_obj.unfreeze_token = None
    encoded_obj.unfreeze_token_created_at = None
    encoded_obj.save()

    messages.success(request, "Image has been unfrozen successfully. Receiver can try decoding again.")
    return redirect("encode")

@login_required
def decode_view(request):
    if request.method == "POST":
        image_id = request.POST.get("image_id", "").strip()
        entered_key = request.POST.get("secret_key", "").strip()

        if not image_id or not entered_key:
            messages.error(request, "Please enter Image ID and Secret Key.")
            return redirect("decode")

        try:
            encoded_obj = EncodedMessage.objects.get(image_id=image_id)

        except EncodedMessage.DoesNotExist:
            messages.error(request, "Invalid Image ID.")
            return redirect("decode")

        if encoded_obj.secret_key_deleted:
            return render(request, "decode.html", {
                "blocked": True,
                "encoded_obj": encoded_obj,
                "message": "The private decoding key for this image has been deleted by the sender."
            })

        if encoded_obj.is_permanently_locked:
            return render(request, "decode.html", {
                "blocked": True,
                "encoded_obj": encoded_obj,
                "message": "This image is frozen due to multiple wrong attempts. Sender confirmation is required to unfreeze it."
            })

        if encoded_obj.is_temp_locked():
            remaining = encoded_obj.temporary_locked_until - timezone.now()
            seconds = max(0, int(remaining.total_seconds()))

            return render(request, "decode.html", {
                "temp_locked": True,
                "remaining_seconds": seconds,
                "encoded_obj": encoded_obj,
                "message": f"Too many wrong attempts. Try again after {seconds} seconds."
            })

        if verify_key(entered_key, encoded_obj.secret_key_hash):
            try:
                encoded_path = encoded_obj.encoded_image.path

                try:
                    encrypted_message = decode_fusion_stego(
                        image_path=encoded_path,
                        secret_key=entered_key
                    )
                except Exception:
                    encrypted_message = encoded_obj.encrypted_message
                decoded_message = decrypt_message(encrypted_message)

                encoded_obj.failed_attempts = 0
                encoded_obj.temporary_locked_until = None
                encoded_obj.is_decoded = True
                encoded_obj.decoded_at = timezone.now()
                encoded_obj.save()

                return render(request, "decode.html", {
                    "success": True,
                    "decoded_message": decoded_message,
                    "encoded_obj": encoded_obj,
                    "show_decode_animation": True,
                })

            except Exception as e:
                messages.error(request, f"Decoding failed: {e}")
                return redirect("decode")

        encoded_obj.failed_attempts += 1

        if encoded_obj.failed_attempts == 3:
            encoded_obj.temporary_locked_until = timezone.now() + timedelta(minutes=2)
            encoded_obj.save()

            send_security_warning_email(
                sender_email=encoded_obj.sender.email,
                sender_username=encoded_obj.sender.username,
                image_id=encoded_obj.image_id,
                failed_attempts=encoded_obj.failed_attempts
            )

            return render(request, "decode.html", {
                "temp_locked": True,
                "remaining_seconds": 120,
                "encoded_obj": encoded_obj,
                "message": "3 wrong attempts detected. Decoding is blocked for 2 minutes. Sender has been alerted."
            })

        if encoded_obj.failed_attempts >= 5:
            token = generate_unfreeze_token()

            encoded_obj.is_permanently_locked = True
            encoded_obj.unfreeze_token = token
            encoded_obj.unfreeze_token_created_at = timezone.now()
            encoded_obj.save()

            unfreeze_url = build_absolute_url(
                request,
                "unfreeze_image",
                token=token
            )

            send_unfreeze_confirmation_email(
                sender_email=encoded_obj.sender.email,
                sender_username=encoded_obj.sender.username,
                image_id=encoded_obj.image_id,
                unfreeze_url=unfreeze_url
            )

            return render(request, "decode.html", {
                "blocked": True,
                "encoded_obj": encoded_obj,
                "message": "5 wrong attempts detected. This image has been frozen. Sender must confirm through email to unfreeze it."
            })

        encoded_obj.save()

        messages.error(
            request,
            f"Wrong Secret Key. Attempt {encoded_obj.failed_attempts}/5."
        )

        return redirect("decode")

    return render(request, "decode.html")

@login_required
def manage_key_view(request):
    if request.method == "POST":
        image_id = request.POST.get("image_id")
        image_key = request.POST.get("image_key")
        action = request.POST.get("action") or request.POST.get("action_hidden")

        if not image_id or not image_key:
            messages.error(request, "Please enter your private Image Key.")
            return redirect("encode")

        try:
            obj = EncodedMessage.objects.get(image_id=image_id, sender=request.user)
        except EncodedMessage.DoesNotExist:
            messages.error(request, "Encoded image not found.")
            return redirect("encode")

        if not verify_key(image_key, obj.image_key_hash):
            messages.error(request, "Invalid Image Key.")
            return redirect("encode")

        if action == "recover_credentials":
            if obj.secret_key_deleted or not obj.secret_key_encrypted:
                messages.error(request, "Private Secret Key has been deleted permanently and cannot be recovered.")
                return redirect("encode")

            request.session["recovered_credentials"] = {
                "encoded_id": obj.id,
                "image_id": obj.image_id,
                "secret_key": decrypt_key_value(obj.secret_key_encrypted),
                "image_key": decrypt_key_value(obj.image_key_encrypted),
                "receiver_email": obj.receiver_email or "Not provided",
            }

            return redirect("encode")

        elif action == "delete_key":
            obj.secret_key_deleted = True
            obj.secret_key_encrypted = None
            obj.save()
            messages.success(request, "Private decoding key deleted permanently.")
            return redirect("encode")

        elif action == "unlock":
            obj.failed_attempts = 0
            obj.temporary_locked_until = None
            obj.is_permanently_locked = False
            obj.unfreeze_token = None
            obj.unfreeze_token_created_at = None
            obj.save()
            messages.success(request, "Image decoding has been unlocked successfully.")
            return redirect("encode")

        messages.error(request, "Invalid management action.")
        return redirect("encode")

    return redirect("encode")




def test_email(request):

    send_mail(
        'Steganography Hub Test',
        'Email system working successfully.',
        settings.EMAIL_HOST_USER,
        ['nadeem.shahzad2512@gmail.com'],
        fail_silently=False,
    )

    return HttpResponse("Email Sent Successfully")


@login_required
def dip_techniques_view(request):
    return render(request, "dip_techniques.html")