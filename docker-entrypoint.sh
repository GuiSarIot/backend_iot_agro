#!/bin/bash

echo "Esperando a que PostgreSQL este listo..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL esta listo!"

echo "Ejecutando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Recolectando archivos estaticos..."
python manage.py collectstatic --noinput --clear

echo "Creando permisos por defecto..."
python manage.py crear_permisos_default

echo "Creando roles por defecto..."
python manage.py crear_roles_default

echo "Configurando MQTT por defecto..."
python manage.py configurar_mqtt_default

echo "Creando superusuario por defecto..."
python manage.py crear_superuser

echo ""
echo "========================================"
echo "Servidor Django iniciando..."
echo "API disponible en: http://localhost:8000/api/"
echo "Admin disponible en: http://localhost:8000/admin/"
echo "Documentacion API: http://localhost:8000/api/docs/"
echo "========================================"
echo ""

exec "$@"
