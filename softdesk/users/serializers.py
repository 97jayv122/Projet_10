"""Serializers for user-related API endpoints."""
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the custom :class:`User` model.

    Exposes basic profile fields and handles password hashing on create/update.
    The ``password`` field is write-only and must contain at least 8 characters.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "age",
            "can_data_be_shared",
            "can_be_contacted",
            "created_at",
        ]

    def create(self, validated_data):
        """Create a new user instance with a hashed password.

        The plaintext password is removed from ``validated_data``,
        hashed via :meth:`User.set_password`, and never stored directly.

        Returns
        -------
        User
            The newly created user.
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update an existing user instance.

        If a ``password`` is provided, it is hashed using
        :meth:`User.set_password` before saving. All other fields are updated
        normally.

        Returns
        -------
        User
            The updated user.
        """
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_age(self, value):
        """Ensure the user is at least 15 years old.

        Parameters
        ----------
        value : int
            The provided age.

        Returns
        -------
        int
            The validated age.
            
        Raises
        ------
        serializers.ValidationError
            If the age is below 15.
        """
        if value < 15:
            raise serializers.ValidationError(
                "Vous devez avoir 15 ans ou plus"
            )
        return value
