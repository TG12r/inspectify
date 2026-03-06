#!/bin/bash

# ============================================================================
# SETUP RÁPIDO - CUANDO YA TIENES TODO EN LA VPS
# ============================================================================
# Ejecutar esto en la VPS paso a paso

echo "🚀 SETUP INSPECTIFY EN VPS"
echo ""

# Asume que estás en /home/root o /home/inspectify/app
APP_HOME=$(pwd)
echo "📁 Carpeta del proyecto: $APP_HOME"
echo ""

# ============================================================================
# 1. CREAR VIRTUAL ENVIRONMENT
# ============================================================================
echo "1️⃣ Creando virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
echo "✓ HECHO"
echo ""

# ============================================================================
# 2. INSTALAR DEPENDENCIAS
# ============================================================================
echo "2️⃣ Instalando dependencias..."
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
echo "✓ HECHO"
echo ""

# ============================================================================
# 3. MIGRACIONES
# ============================================================================
echo "3️⃣ Ejecutando migraciones..."
python manage.py migrate
echo "✓ HECHO"
echo ""

# ============================================================================
# 4. STATIC FILES
# ============================================================================
echo "4️⃣ Recolectando static files..."
python manage.py collectstatic --noinput
echo "✓ HECHO"
echo ""

# ============================================================================
# 5. CREAR DIRECTORIOS
# ============================================================================
echo "5️⃣ Creando directorios de logs..."
mkdir -p logs
mkdir -p backups
echo "✓ HECHO"
echo ""

# ============================================================================
# 6. TEST DE LA APP
# ============================================================================
echo "6️⃣ Verificando que todo esté OK..."
python manage.py check
echo "✓ HECHO"
echo ""

echo "════════════════════════════════════════════════════════"
echo "✓ SETUP COMPLETADO"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Próximo paso: Crear superusuario"
echo "python manage.py createsuperuser"
echo ""
echo "Luego: Configurar Gunicorn + Nginx"
echo "Ver: VPS_DEPLOYMENT_GUIDE.md"
echo ""
