from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=extra_fields.get("name", ""),
            contact_no=extra_fields.get("contact_no", ""),
            is_admin=extra_fields.get("is_admin", False),
            is_staff=extra_fields.get("is_staff", False),
            is_superuser=extra_fields.get("is_superuser", False),
            is_active=True,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        SUPERUSER - Django Admin + Dashboard dono access
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)  # Dashboard bhi access
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def create_admin(self, email, password=None, **extra_fields):
        """
        ADMIN - Sirf Dashboard access, Django Admin nahi
        """
        extra_fields.setdefault("is_staff", False)      # Django Admin nahi
        extra_fields.setdefault("is_superuser", False)  # Superuser nahi
        extra_fields.setdefault("is_admin", True)       # Dashboard access
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email        = models.EmailField(unique=True)
    name         = models.CharField(max_length=100, blank=True, null=True)
    contact_no   = models.CharField(max_length=15, blank=True, null=True)

    # Role flags
    is_admin     = models.BooleanField(default=False)       # Dashboard access
    is_staff     = models.BooleanField(default=False)       # Django admin access
    is_superuser = models.BooleanField(default=False)   # Full permissions
    is_active    = models.BooleanField(default=True)

    # Track who created this admin
    created_by   = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_admins'
    )
    created_at   = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def role(self):
        if self.is_superuser:
            return "superuser"
        elif self.is_admin:
            return "admin"
        return "user"

    def can_create_admin(self):
        """Sirf superuser admin create kar sakta hai"""
        return self.is_superuser

    def can_create_employee(self):
        """Admin aur superuser dono employee create kar sakte hain"""
        return self.is_admin or self.is_superuser


class Employee(models.Model):
    name        = models.CharField(max_length=100)
    email       = models.EmailField()
    address     = models.TextField()
    designation = models.CharField(max_length=100)
    contact_no  = models.CharField(max_length=15)
    
    # Track who created this employee
    created_by  = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_employees'
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Enquiry(models.Model):
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    company    = models.CharField(max_length=100)
    service    = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)    