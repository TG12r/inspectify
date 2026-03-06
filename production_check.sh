#!/bin/bash

# Script para verificar que el proyecto esté listo para producción
# Uso: ./production_check.sh

echo "🔍 Verificando proyecto para producción..."
echo ""

ERRORS=0
WARNINGS=0

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Verificar que no sea DEBUG=True
echo "1. Verificando DEBUG..."
if grep -q "DEBUG.*True" .env 2>/dev/null; then
    echo -e "${RED}✗ ERROR: DEBUG está en True en .env${NC}"
    ((ERRORS++))
else
    echo -e "${GREEN}✓ DEBUG está en False${NC}"
fi
echo ""

# 2. Verificar que hay SECRET_KEY
echo "2. Verificando SECRET_KEY..."
if grep -q "SECRET_KEY=" .env && ! grep -q "SECRET_KEY=$" .env; then
    echo -e "${GREEN}✓ SECRET_KEY está configurado${NC}"
else
    echo -e "${RED}✗ ERROR: SECRET_KEY no está configurado${NC}"
    ((ERRORS++))
fi
echo ""

# 3. Verificar ALLOWED_HOSTS
echo "3. Verificando ALLOWED_HOSTS..."
if grep -q "ALLOWED_HOSTS=" .env; then
    echo -e "${GREEN}✓ ALLOWED_HOSTS está configurado${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: ALLOWED_HOSTS podría no estar en .env${NC}"
    ((WARNINGS++))
fi
echo ""

# 4. Verificar base de datos
echo "4. Verificando configuración de base de datos..."
if grep -q "DATABASE_NAME=" .env; then
    echo -e "${GREEN}✓ Base de datos configurada${NC}"
else
    echo -e "${RED}✗ ERROR: Base de datos no configurada${NC}"
    ((ERRORS++))
fi
echo ""

# 5. Verificar requirements.txt
echo "5. Verificando requirements.txt..."
if [ -f requirements.txt ]; then
    PACKAGES=$(wc -l < requirements.txt)
    echo -e "${GREEN}✓ requirements.txt existe ($PACKAGES paquetes)${NC}"
else
    echo -e "${RED}✗ ERROR: requirements.txt no existe${NC}"
    ((ERRORS++))
fi
echo ""

# 6. Verificar Static files
echo "6. Verificando configuración de static files..."
if grep -q "STATIC_ROOT" inspectify/settings.py; then
    echo -e "${GREEN}✓ STATIC_ROOT configurado${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: STATIC_ROOT podría no estar configurado${NC}"
    ((WARNINGS++))
fi
echo ""

# 7. Verificar .env no está en git
echo "7. Verificando que .env no esté en git..."
if grep -q ".env" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✓ .env está en .gitignore${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: .env podría estar en git${NC}"
    ((WARNINGS++))
fi
echo ""

# 8. Verificar que .env.example existe
echo "8. Verificando .env.example..."
if [ -f .env.example ]; then
    echo -e "${GREEN}✓ .env.example existe${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: .env.example no existe${NC}"
    ((WARNINGS++))
fi
echo ""

# 9. Verificar gunicorn_config.py
echo "9. Verificando gunicorn_config.py..."
if [ -f gunicorn_config.py ]; then
    echo -e "${GREEN}✓ gunicorn_config.py existe${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: gunicorn_config.py no existe${NC}"
    ((WARNINGS++))
fi
echo ""

# 10. Verificar nginx.conf
echo "10. Verificando nginx.conf..."
if [ -f nginx.conf ]; then
    echo -e "${GREEN}✓ nginx.conf existe${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: nginx.conf no existe${NC}"
    ((WARNINGS++))
fi
echo ""

# 11. Verificar DEPLOYMENT.md
echo "11. Verificando documentación..."
if [ -f DEPLOYMENT.md ]; then
    echo -e "${GREEN}✓ DEPLOYMENT.md existe${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: DEPLOYMENT.md no existe${NC}"
    ((WARNINGS++))
fi
echo ""

# Resumen
echo "=========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ ¡Proyecto listo para producción!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Proyecto casi listo ($WARNINGS advertencias)${NC}"
    exit 0
else
    echo -e "${RED}✗ Se encontraron $ERRORS errores y $WARNINGS advertencias${NC}"
    echo "Por favor, corrige los errores antes de desplegar"
    exit 1
fi
