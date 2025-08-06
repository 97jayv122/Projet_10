from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'age', 'can_data_be_shared','can_be_contacted', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def validate_age(self, value):
        """
        """
        if value < 15:
            raise serializers.ValidationError(
                'Vous devez avoir 15 ans ou plus'
                )
        return value
    
    def validate(self, attrs):
        if self.instance is None:
            if not attrs.get('can_be_contacted', False):
                raise serializers.ValidationError(
                    {'can_be_contacted': 'Le consentement pour être contacté est requis'}
                )       
            if not attrs.get('can_data_be_shared', False):
                raise serializers.ValidationError(
                    {'can_data_be_shared': 'Le consentement sur l\'utilisation des données est requis'}
                )
        return attrs