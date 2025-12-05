#!/bin/bash

echo "========================================"
echo "IoT Sensor Platform - Docker"
echo "========================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${YELLOW}1. Verificando archivo .env...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "${GREEN}✓ Archivo .env creado${NC}"
    echo "${YELLOW}⚠️  IMPORTANTE: Revisa el archivo .env antes de continuar${NC}"
    echo "${YELLOW}Presiona Enter para continuar...${NC}"
    read
else
    echo "${GREEN}✓ Archivo .env existe${NC}"
fi
echo ""

echo "${YELLOW}2. Deteniendo contenedores existentes...${NC}"
docker-compose down
echo ""

echo "${YELLOW}3. Construyendo y levantando contenedores...${NC}"
docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo "${RED}✗ Error al levantar contenedores${NC}"
    exit 1
fi

echo "${GREEN}✓ Contenedores levantados${NC}"
echo ""

echo "${YELLOW}4. Esperando a que los servicios estén listos...${NC}"
sleep 10
echo ""

echo "${YELLOW}5. ¿Deseas crear un superusuario? (s/n)${NC}"
read -p "Respuesta: " crear_super

if [ "$crear_super" = "s" ] || [ "$crear_super" = "S" ]; then
    docker-compose exec django python manage.py crear_superuser
fi

echo ""
echo "${YELLOW}6. ¿Deseas crear datos de prueba? (s/n)${NC}"
read -p "Respuesta: " crear_datos

if [ "$crear_datos" = "s" ] || [ "$crear_datos" = "S" ]; then
    docker-compose exec django python manage.py crear_datos_prueba
fi

echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}✓ ¡Sistema iniciado!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "Servicios disponibles:"
echo "  - API: http://localhost:8000/api/"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - Docs: http://localhost:8000/api/docs/"
echo "  - PostgreSQL: localhost:5432"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: ${YELLOW}docker-compose logs -f django${NC}"
echo "  - Ejecutar comando: ${YELLOW}docker-compose exec django python manage.py <comando>${NC}"
echo "  - Detener: ${YELLOW}docker-compose down${NC}"
echo "  - Reiniciar: ${YELLOW}docker-compose restart${NC}"
echo ""
echo "${YELLOW}⚠️  NOTA: localhost se refiere a la máquina que ejecuta Docker${NC}"
echo ""
