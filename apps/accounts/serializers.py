from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'bio', 'avatar', 'is_staff', 'is_active', 'date_joined')
        read_only_fields = ('id', 'role', 'is_staff', 'date_joined')


class ManagerUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 'bio',
            'avatar', 'is_staff', 'is_active', 'date_joined', 'password'
        )
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        password = validated_data.pop('password', None) or 'vaxshop123'
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'role')
        read_only_fields = ('id',)

    def validate_role(self, value):
        # Public registration can only create customers. Managers are promoted in admin panel.
        if value == User.Role.MANAGER:
            raise serializers.ValidationError('Manager accounts must be created by another manager.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = User.Role.CUSTOMER
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
