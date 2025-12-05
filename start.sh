#!/bin/bash

echo "========================================"
echo "IoT Sensor Platform - Inicio Rápido"
echo "========================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${YELLOW}1. Instalando dependencias...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "${RED}✗ Error instalando dependencias${NC}"
    exit 1
fi

echo "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

echo "${YELLOW}2. Copiando archivo de configuración...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "${GREEN}✓ Archivo .env creado${NC}"
    echo "${YELLOW}⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones${NC}"
else
    echo "${GREEN}✓ Archivo .env ya existe${NC}"
fi
echo ""

echo "${YELLOW}3. Ejecutando migraciones...${NC}"
python manage.py makemigrations
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "${RED}✗ Error en migraciones${NC}"
    echo "${YELLOW}Asegúrate de que PostgreSQL esté corriendo y configurado correctamente${NC}"
    exit 1
fi

echo "${GREEN}✓ Migraciones completadas${NC}"
echo ""

echo "${YELLOW}4. Creando roles y permisos...${NC}"
python manage.py crear_permisos_default
python manage.py crear_roles_default
echo "${GREEN}✓ Roles y permisos creados${NC}"
echo ""

echo "${YELLOW}5. ¿Deseas crear un superusuario? (s/n)${NC}"
read -p "Respuesta: " crear_super

if [ "$crear_super" = "s" ] || [ "$crear_super" = "S" ]; then
    python manage.py crear_superuser
fi

echo ""
echo "${YELLOW}6. ¿Deseas crear datos de prueba? (s/n)${NC}"
read -p "Respuesta: " crear_datos

if [ "$crear_datos" = "s" ] || [ "$crear_datos" = "S" ]; then
    python manage.py crear_datos_prueba
fi

echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}✓ ¡Configuración completada!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "Para iniciar el servidor:"
echo "  ${YELLOW}python manage.py runserver 0.0.0.0:8000${NC}"
echo ""
echo "Endpoints disponibles:"
echo "  - API: http://localhost:8000/api/"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - Docs: http://localhost:8000/api/docs/"
echo ""
echo "${YELLOW}⚠️  NOTA: localhost se refiere a la máquina que ejecuta el servidor${NC}"
echo ""
