#!/bin/bash

# ============================================================================
# DEPLOY AUTOMÁTICO INSPECTIFY A VPS
# ============================================================================
# USO:
# 1. Copiar este script al servidor: scp deploy.sh user@ip:/home/user/
# 2. SSH al servidor: ssh user@ip
# 3. Ejecutar: bash deploy.sh
# ============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        DEPLOY AUTOMÁTICO INSPECTIFY A PRODUCCIÓN            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
APP_USER="inspectify"
APP_HOME="/home/$APP_USER/app"
APP_DOMAIN="${1:-tudominio.com}"
APP_EMAIL="admin@${APP_DOMAIN}"

# Función para imprimir secciones
print_section() {
    echo -e "\n${BLUE}►► $1${NC}\n"
}

# ============================================================================
# 1. ACTUALIZAR SISTEMA
# ============================================================================
print_section "1. ACTUALIZANDO SISTEMA"

sudo apt update
sudo apt upgrade -y
sudo apt install -y \
    build-essential \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    supervisor \
    curl \
    certbot \
    python3-certbot-nginx \
    nano \
    htop

echo -e "${GREEN}✓ Sistema actualizado${NC}"

# ============================================================================
# 2. CREAR USUARIO PARA LA APP
# ============================================================================
print_section "2. CREANDO USUARIO DE APLICACIÓN"

if id "$APP_USER" &>/dev/null; then
    echo -e "${YELLOW}⚠ Usuario $APP_USER ya existe${NC}"
else
    sudo useradd -m -s /bin/bash $APP_USER
    echo -e "${GREEN}✓ Usuario $APP_USER creado${NC}"
fi

# ============================================================================
# 3. CONFIGURAR POSTGRESQL
# ============================================================================
print_section "3. CONFIGURANDO POSTGRESQL"

DB_NAME="inspectify_db"
DB_USER="inspectify_user"
DB_PASSWORD=$(openssl rand -base64 32)

sudo -u postgres psql <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET default_transaction_deferrable TO on;
ALTER ROLE $DB_USER SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo -e "${GREEN}✓ PostgreSQL configurado${NC}"
echo -e "${YELLOW}Database User: $DB_USER${NC}"
echo -e "${YELLOW}Database Password: $DB_PASSWORD${NC}"
echo ""

# ============================================================================
# 4. CLONAR PROYECTO
# ============================================================================
print_section "4. CLONANDO PROYECTO"

if [ -z "$GIT_REPO" ]; then
    echo -e "${RED}ERROR: Debes pasare el git repo${NC}"
    echo "Uso: bash deploy.sh tudominio.com https://github.com/user/repo.git"
    exit 1
fi

GIT_REPO="${2:-https://github.com/user/inspectify.git}"

sudo mkdir -p $APP_HOME
sudo chown $APP_USER:$APP_USER $APP_HOME

sudo -u $APP_USER git clone $GIT_REPO $APP_HOME
cd $APP_HOME

echo -e "${GREEN}✓ Proyecto clonado${NC}"

# ============================================================================
# 5. CREAR VIRTUAL ENVIRONMENT
# ============================================================================
print_section "5. CREANDO VIRTUAL ENVIRONMENT"

sudo -u $APP_USER python3 -m venv $APP_HOME/venv
sudo -u $APP_USER $APP_HOME/venv/bin/pip install --upgrade pip setuptools wheel

echo -e "${GREEN}✓ Virtual environment creado${NC}"

# ============================================================================
# 6. INSTALAR DEPENDENCIAS
# ============================================================================
print_section "6. INSTALANDO DEPENDENCIAS"

sudo -u $APP_USER $APP_HOME/venv/bin/pip install -r $APP_HOME/requirements.txt
sudo -u $APP_USER $APP_HOME/venv/bin/pip install gunicorn

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# ============================================================================
# 7. CONFIGURAR VARIABLES DE ENTORNO
# ============================================================================
print_section "7. CONFIGURANDO .env"

# Generar SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Crear .env
sudo -u $APP_USER cat > $APP_HOME/.env <<EOF
# Django Settings
SECRET_KEY='$SECRET_KEY'
DEBUG=False
ALLOWED_HOSTS=$APP_DOMAIN,www.$APP_DOMAIN,localhost,127.0.0.1

# Database
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=5432

# External APIs
GEMINI_API_KEY=your-gemini-api-key-here

# Email (Configurar después)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@$APP_DOMAIN
EOF

sudo chmod 600 $APP_HOME/.env
echo -e "${GREEN}✓ .env configurado${NC}"

# ============================================================================
# 8. EJECUTAR MIGRACIONES
# ============================================================================
print_section "8. EJECUTANDO MIGRACIONES"

cd $APP_HOME
sudo -u $APP_USER $APP_HOME/venv/bin/python manage.py migrate

echo -e "${GREEN}✓ Migraciones completadas${NC}"

# ============================================================================
# 9. RECOLECTAR STATIC FILES
# ============================================================================
print_section "9. RECOLECTANDO STATIC FILES"

cd $APP_HOME
sudo -u $APP_USER $APP_HOME/venv/bin/python manage.py collectstatic --noinput

echo -e "${GREEN}✓ Static files recolectados${NC}"

# ============================================================================
# 10. CREAR DIRECTORIO DE LOGS
# ============================================================================
print_section "10. CREANDO DIRECTORIOS"

sudo mkdir -p /home/$APP_USER/logs
sudo chown $APP_USER:$APP_USER /home/$APP_USER/logs
sudo chmod 755 /home/$APP_USER/logs

echo -e "${GREEN}✓ Directorios creados${NC}"

# ============================================================================
# 11. CONFIGURAR GUNICORN (systemd)
# ============================================================================
print_section "11. CONFIGURANDO GUNICORN"

sudo tee /etc/systemd/system/inspectify.service > /dev/null <<EOF
[Unit]
Description=Inspectify Django Application
After=network.target postgresql.service

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_HOME
ExecStart=$APP_HOME/venv/bin/gunicorn \\
    --workers 4 \\
    --bind 127.0.0.1:8000 \\
    --timeout 30 \\
    --access-logfile /home/$APP_USER/logs/access.log \\
    --error-logfile /home/$APP_USER/logs/error.log \\
    inspectify.wsgi:application

Restart=always
RestartSec=10
StandardOutput=append:/home/$APP_USER/logs/gunicorn.log
StandardError=append:/home/$APP_USER/logs/gunicorn.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable inspectify.service
sudo systemctl start inspectify.service

echo -e "${GREEN}✓ Gunicorn configurado${NC}"

# ============================================================================
# 12. CONFIGURAR NGINX
# ============================================================================
print_section "12. CONFIGURANDO NGINX"

sudo tee /etc/nginx/sites-available/inspectify > /dev/null <<EOF
upstream inspectify_app {
    server 127.0.0.1:8000 fail_timeout=10s;
}

server {
    listen 80;
    server_name $APP_DOMAIN www.$APP_DOMAIN;

    client_max_body_size 100M;

    location / {
        proxy_pass http://inspectify_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $APP_HOME/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias $APP_HOME/media/;
        expires 7d;
    }
}
EOF

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/inspectify /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar sintaxis
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

echo -e "${GREEN}✓ Nginx configurado${NC}"

# ============================================================================
# 13. INSTALAR SSL CON CERTBOT
# ============================================================================
print_section "13. INSTALANDO CERTIFICADO SSL"

echo -e "${YELLOW}Se abrirá un diálogo de Certbot...${NC}"

sudo certbot --nginx \
    -d $APP_DOMAIN \
    -d www.$APP_DOMAIN \
    --email $APP_EMAIL \
    --agree-tos \
    --non-interactive \
    --redirect

echo -e "${GREEN}✓ Certificado SSL instalado${NC}"

# ============================================================================
# 14. CONFIGURAR FIREWALL
# ============================================================================
print_section "14. CONFIGURANDO FIREWALL"

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo -e "${GREEN}✓ Firewall configurado${NC}"

# ============================================================================
# 15. CONFIGURAR BACKUP AUTOMÁTICO
# ============================================================================
print_section "15. CONFIGURANDO BACKUP AUTOMÁTICO"

sudo mkdir -p /home/$APP_USER/backups
sudo chown $APP_USER:$APP_USER /home/$APP_USER/backups

# Copiar script de backup
sudo -u $APP_USER tee $APP_HOME/backup_db.sh > /dev/null <<'BACKUP_SCRIPT'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/inspectify/backups"
mkdir -p $BACKUP_DIR
pg_dump -h localhost -U inspectify_user inspectify_db > $BACKUP_DIR/inspectify_db_$DATE.sql
gzip $BACKUP_DIR/inspectify_db_$DATE.sql
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete
echo "Backup completado: $BACKUP_DIR/inspectify_db_$DATE.sql.gz"
BACKUP_SCRIPT

sudo chmod +x $APP_HOME/backup_db.sh

# Agregar a crontab
CRON_ENTRY="0 2 * * * /home/$APP_USER/app/backup_db.sh"
(sudo -u $APP_USER crontab -l 2>/dev/null || true; echo "$CRON_ENTRY") | sudo -u $APP_USER crontab -

echo -e "${GREEN}✓ Backup automático configurado (diariamente a las 2 AM)${NC}"

# ============================================================================
# 16. CREAR SUPERUSUARIO
# ============================================================================
print_section "16. CREANDO SUPERUSUARIO"

echo -e "${YELLOW}Ingresa datos para el superusuario:${NC}"

cd $APP_HOME
sudo -u $APP_USER $APP_HOME/venv/bin/python manage.py createsuperuser

echo -e "${GREEN}✓ Superusuario creado${NC}"

# ============================================================================
# RESUMEN FINAL
# ============================================================================
clear
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          ✓ DEPLOY COMPLETADO EXITOSAMENTE                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Tu aplicación está en PRODUCCIÓN${NC}"
echo ""
echo "📍 URL: ${BLUE}https://$APP_DOMAIN${NC}"
echo "🔐 Admin: ${BLUE}https://$APP_DOMAIN/admin${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "DATABASE CREDENTIALS (GUARDAR EN UN LUGAR SEGURO):"
echo "═══════════════════════════════════════════════════════════"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo "Host: localhost"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PRÓXIMOS PASOS:"
echo "═══════════════════════════════════════════════════════════"
echo "1. Acceder a admin: https://$APP_DOMAIN/admin"
echo "2. Actualizar GEMINI_API_KEY en .env:"
echo "   nano $APP_HOME/.env"
echo "   Luego: systemctl restart inspectify"
echo ""
echo "3. Ver logs:"
echo "   tail -f /home/$APP_USER/logs/error.log"
echo ""
echo "4. Comandos útiles:"
echo "   sudo systemctl status inspectify      # Estado de la app"
echo "   sudo systemctl restart inspectify     # Reiniciar app"
echo "   sudo systemctl restart nginx          # Reiniciar Nginx"
echo "   sudo journalctl -u inspectify -f      # Ver logs en tiempo real"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
