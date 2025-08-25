"""Custom user model for the SoftDesk API."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extend Django’s :class:`AbstractUser` with profile and consent fields.

    Attributes
    ----------
    age : models.PositiveSmallIntegerField
        User’s age in years. (Validation for minimum age is handled in the serializer.)
    can_be_contacted : models.BooleanField
        Whether the user agrees to be contacted (e.g., updates, support).
    can_data_be_shared : models.BooleanField
        Whether the user consents to data sharing for analytics/metrics.
    created_at : models.DateTimeField
        Timestamp automatically set when the account is created.
    """

    age = models.PositiveSmallIntegerField()
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
