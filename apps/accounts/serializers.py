"""
Serializers para la app Accounts
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Rol, Permiso


# ============ Serializers de Autenticación ============

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'tipo_usuario', 'rol'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden."}
            )
        return attrs
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            tipo_usuario=validated_data.get('tipo_usuario', 'externo'),
            rol=validated_data.get('rol', None)
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer para el login de usuarios
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    'No se puede iniciar sesión con las credenciales proporcionadas.'
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    'Esta cuenta de usuario está desactivada.'
                )
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe incluir "username" y "password".'
            )


# ============ Serializers de Modelos ============

class PermisoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Permiso
    """
    class Meta:
        model = Permiso
        fields = ['id', 'nombre', 'codigo', 'descripcion', 'created_at']
        read_only_fields = ['created_at']


class RolSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Rol
    """
    permisos = PermisoSerializer(many=True, read_only=True)
    permisos_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permiso.objects.all(),
        write_only=True,
        source='permisos',
        required=False
    )
    nombre_display = serializers.CharField(source='get_nombre_display', read_only=True)
    
    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'nombre_display', 'descripcion',
            'permisos', 'permisos_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo CustomUser
    """
    rol_detail = RolSerializer(source='rol', read_only=True)
    tipo_usuario_display = serializers.CharField(
        source='get_tipo_usuario_display',
        read_only=True
    )
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'tipo_usuario', 'tipo_usuario_display',
            'is_active', 'is_staff', 'is_superuser', 'rol',
            'rol_detail', 'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class CustomUserCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar usuarios
    """
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'first_name',
            'last_name', 'tipo_usuario', 'is_active', 'rol'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
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
