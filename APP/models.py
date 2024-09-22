from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.
class guest_url(models.Model):
    rurl = models.CharField(max_length=30)
    ourl = models.TextField()
    created_at = models.TextField(max_length=30)
    expiry_at = models.TextField(max_length=30)

    def __str__(self):
        return f"{self.id} - {self.rurl}"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(verbose_name="Email Address", unique=True)
    username = models.CharField(max_length=30, unique=True)
    contact = models.CharField(max_length=20, blank=True)
    image = models.ImageField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = CustomUserManager()

    def delete(self, *args, **kwargs):
        if self.image != "default_pic.png":
            self.image.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class Public_URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_url = models.CharField(max_length=255)
    long_url = models.CharField(max_length=500)
    Created_at = models.CharField(max_length=50)
    clicks = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.short_url}"


class Public_URL_Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.ForeignKey(Public_URL, on_delete=models.CASCADE)
    url_log = models.CharField(max_length=50)
    clicks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.url} - {self.url_log}"


class Private_URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_url = models.CharField(max_length=255)
    long_url = models.CharField(max_length=500)
    url_password = models.CharField(max_length=50)
    Created_at = models.CharField(max_length=50)
    clicks = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.short_url} - {self.url_password}"


class Private_URL_Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.ForeignKey(Private_URL, on_delete=models.CASCADE)
    url_log = models.CharField(max_length=50)
    clicks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.url} - {self.url_log}"


class Custom_URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    short_url = models.CharField(max_length=255)
    long_url = models.CharField(max_length=500)
    Created_at = models.CharField(max_length=50)
    clicks = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.short_url}"


class Custom_URL_Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.ForeignKey(Custom_URL, on_delete=models.CASCADE)
    url_log = models.CharField(max_length=50)
    clicks = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.url} - {self.url_log}"
