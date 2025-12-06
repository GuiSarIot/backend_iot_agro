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
    can_receive_telegram = serializers.BooleanField(
        source='can_receive_telegram_notifications',
        read_only=True
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'tipo_usuario', 'tipo_usuario_display',
            'is_active', 'is_staff', 'is_superuser', 'rol',
            'rol_detail', 'created_at', 'updated_at', 'last_login',
            # Telegram fields
            'telegram_chat_id', 'telegram_username', 'telegram_notifications_enabled',
            'telegram_verified', 'can_receive_telegram'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'last_login', 
            'telegram_verified', 'can_receive_telegram'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'telegram_chat_id': {'read_only': True}  # Solo el bot puede establecerlo
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
            'last_name', 'tipo_usuario', 'is_active', 'rol',
            'telegram_username', 'telegram_notifications_enabled'
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


# ============ Serializers de Auditoría ============

class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer para registros de auditoría (solo lectura)
    """
    user_display = serializers.CharField(source='username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = 'accounts.AuditLog'
        fields = [
            'id', 'user', 'user_display', 'username', 'model_name',
            'object_id', 'object_repr', 'action', 'action_display',
            'changes', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = fields
    
    def to_representation(self, instance):
        from .models import AuditLog
        if not isinstance(instance, AuditLog):
            instance = AuditLog.objects.get(pk=instance.pk)
        return super().to_representation(instance)


class AccessLogSerializer(serializers.ModelSerializer):
    """
    Serializer para registros de acceso a módulos
    """
    user_display = serializers.CharField(source='username', read_only=True)
    module_display = serializers.CharField(source='get_module_display', read_only=True)
    is_error = serializers.BooleanField(read_only=True)
    is_slow = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = 'accounts.AccessLog'
        fields = [
            'id', 'user', 'user_display', 'username', 'module',
            'module_display', 'endpoint', 'method', 'status_code',
            'ip_address', 'user_agent', 'response_time_ms',
            'query_params', 'metadata', 'timestamp', 'is_error', 'is_slow'
        ]
        read_only_fields = fields
    
    def to_representation(self, instance):
        from .models import AccessLog
        if not isinstance(instance, AccessLog):
            instance = AccessLog.objects.get(pk=instance.pk)
        return super().to_representation(instance)


class CreateAccessLogSerializer(serializers.ModelSerializer):
    """
    Serializer para crear registros de acceso (write-only)
    """
    class Meta:
        model = 'accounts.AccessLog'
        fields = [
            'module', 'endpoint', 'method', 'status_code',
            'ip_address', 'user_agent', 'response_time_ms',
            'query_params', 'metadata'
        ]
    
    def create(self, validated_data):
        from .models import AccessLog
        # Agregar usuario del contexto
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            validated_data['user'] = user if user.is_authenticated else None
            validated_data['username'] = user.username if user.is_authenticated else 'anonymous'
        else:
            validated_data['username'] = 'system'
        
        return AccessLog.objects.create(**validated_data)


# ============ Serializers de Telegram ============

class TelegramVerificationSerializer(serializers.Serializer):
    """
    Serializer para generar código de verificación de Telegram
    """
    pass


class TelegramVerifyCodeSerializer(serializers.Serializer):
    """
    Serializer para verificar código de Telegram
    """
    code = serializers.CharField(
        max_length=10,
        required=True,
        help_text='Código de verificación recibido'
    )


class TelegramLinkSerializer(serializers.Serializer):
    """
    Serializer para vincular cuenta de Telegram (usado por el bot)
    """
    user_id = serializers.IntegerField(required=True)
    chat_id = serializers.CharField(max_length=50, required=True)
    username = serializers.CharField(max_length=100, required=False, allow_blank=True)
    verification_code = serializers.CharField(max_length=10, required=True)


class TelegramNotificationSerializer(serializers.Serializer):
    """
    Serializer para enviar notificación via Telegram
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='IDs de usuarios específicos (opcional)'
    )
    message = serializers.CharField(
        required=True,
        help_text='Mensaje a enviar'
    )
    notification_type = serializers.ChoiceField(
        choices=[
            ('info', 'Información'),
            ('warning', 'Advertencia'),
            ('error', 'Error'),
            ('success', 'Éxito'),
        ],
        default='info',
        required=False
    )
    send_to_all_verified = serializers.BooleanField(
        default=False,
        help_text='Enviar a todos los usuarios verificados'
    )


# ============ Serializers de Email ============

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer para enviar email de verificación
    """
    pass


class EmailVerifyTokenSerializer(serializers.Serializer):
    """
    Serializer para verificar token de email
    """
    token = serializers.CharField(
        max_length=100,
        required=True,
        help_text='Token de verificación recibido por email'
    )


class EmailNotificationSerializer(serializers.Serializer):
    """
    Serializer para enviar notificación via Email
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='IDs de usuarios específicos (opcional)'
    )
    message = serializers.CharField(
        required=True,
        help_text='Mensaje a enviar'
    )
    subject = serializers.CharField(
        required=False,
        help_text='Asunto del email (opcional, se genera automáticamente)'
    )
    notification_type = serializers.ChoiceField(
        choices=[
            ('info', 'Información'),
            ('warning', 'Advertencia'),
            ('error', 'Error'),
            ('success', 'Éxito'),
        ],
        default='info',
        required=False
    )
    send_to_all_verified = serializers.BooleanField(
        default=False,
        help_text='Enviar a todos los usuarios con email verificado'
    )


class EmailPreferencesSerializer(serializers.Serializer):
    """
    Serializer para actualizar preferencias de notificaciones por email
    """
    email_notifications_enabled = serializers.BooleanField(
        required=False,
        help_text='Habilitar/deshabilitar notificaciones por email'
    )
