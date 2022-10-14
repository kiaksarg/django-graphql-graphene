from typing import Union

from django.conf import settings
from django.contrib.auth.models import _user_has_perm  # type: ignore
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
# from django.contrib.postgres.fields import JSONField
from django.db import models
# from django.db.models import JSONField  # type: ignore
from django.db.models import Q, QuerySet, Value
from django.forms.models import model_to_dict
from django.utils import timezone
from django_countries.fields import Country, CountryField
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from versatileimagefield.fields import VersatileImageField
from django.utils.crypto import get_random_string

from ..core.models import ModelWithMetadata
from ..core.permissions import AccountPermissions, BasePermissionEnum, get_permissions
from ..core.utils.json_serializer import CustomJsonEncoder
from . import CustomerEvents
from .validators import validate_possible_number


class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


class UserManager(BaseUserManager):
    def create_user(
        self, email, password=None, is_staff=False, is_active=True, **extra_fields
    ):
        """Create a user instance with the given email and password."""
        email = UserManager.normalize_email(email)
        # Google OAuth2 backend send unnecessary username field
        extra_fields.pop("username", None)

        user = self.model(
            email=email, is_active=is_active, is_staff=is_staff, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields
        )

    # def customers(self):
    #     return self.get_queryset().filter(
    #         Q(is_staff=False) | (Q(is_staff=True) & Q(orders__isnull=False))
    #     )
    def users(self):
        return self.get_queryset().filter(is_staff=False)

    def staff(self):
        return self.get_queryset().filter(is_staff=True)


class User(PermissionsMixin, ModelWithMetadata, AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    phone = PossiblePhoneNumberField(blank=True, default="")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    avatar = VersatileImageField(
        upload_to="user-avatars", blank=True, null=True)
    jwt_token_key = models.CharField(max_length=12, default=get_random_string)

    USERNAME_FIELD = "email"

    objects = UserManager()

    class Meta:
        ordering = ("email",)
        permissions = (
            (AccountPermissions.MANAGE_USERS.codename, "Manage customers."),
            (AccountPermissions.MANAGE_STAFF.codename, "Manage staff."),
        )

    def get_full_name(self):
        if self.first_name or self.last_name:
            return ("%s %s" % (self.first_name, self.last_name)).strip()

        return self.email

    def get_short_name(self):
        return self.email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._effective_permissions = None

    @property
    def effective_permissions(self) -> "QuerySet[Permission]":
        if self._effective_permissions is None:
            self._effective_permissions = get_permissions()
            if not self.is_superuser:
                self._effective_permissions = self._effective_permissions.filter(
                    Q(user=self) | Q(group__user=self)
                )
        return self._effective_permissions

    @effective_permissions.setter
    def effective_permissions(self, value: "QuerySet[Permission]"):
        self._effective_permissions = value
        # Drop cache for authentication backend
        self._effective_permissions_cache = None

    def has_perm(self, perm: Union[BasePermissionEnum, str], obj=None):  # type: ignore
        # This method is overridden to accept perm as BasePermissionEnum
        perm = perm.value if hasattr(perm, "value") else perm  # type: ignore

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser and not self._effective_permissions:
            return True
        return _user_has_perm(self, perm, obj)
