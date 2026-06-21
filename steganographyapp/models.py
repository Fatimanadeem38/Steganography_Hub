from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class EncodedMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    image_id = models.CharField(max_length=30, unique=True)
    original_image_name = models.CharField(max_length=255)
    encoded_image = models.ImageField(upload_to="encoded_images/")

    secret_key_hash = models.CharField(max_length=255)
    image_key_hash = models.CharField(max_length=255)

    # NEW: encrypted recoverable keys
    secret_key_encrypted = models.TextField(null=True, blank=True)
    image_key_encrypted = models.TextField(null=True, blank=True)

    encrypted_message = models.TextField()

    receiver_email = models.EmailField(null=True, blank=True)

    mse_value = models.FloatField(null=True, blank=True)
    psnr_value = models.FloatField(null=True, blank=True)
    ssim_value = models.FloatField(null=True, blank=True)

    failed_attempts = models.IntegerField(default=0)
    temporary_locked_until = models.DateTimeField(null=True, blank=True)
    is_permanently_locked = models.BooleanField(default=False)
    unfreeze_token = models.CharField(max_length=120, null=True, blank=True)
    unfreeze_token_created_at = models.DateTimeField(null=True, blank=True)
    secret_key_deleted = models.BooleanField(default=False)

    # NEW: decoded status
    is_decoded = models.BooleanField(default=False)
    decoded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_temp_locked(self):
        return (
            self.temporary_locked_until is not None
            and self.temporary_locked_until > timezone.now()
        )

    def __str__(self):
        return self.image_id