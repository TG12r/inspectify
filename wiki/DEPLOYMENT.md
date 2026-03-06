# Guía de Deployment a Producción - Inspectify

## 📋 Checklist Pre-Deployment

### 1. Configuración Inicial
- [ ] Crear servidor Linux (Ubuntu 20.04 LTS recomendado)
- [ ] Actualizar sistema: `sudo apt update && sudo apt upgrade`
- [ ] Instalar dependencias del sistema:
```bash
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx git supervisor certbot python3-certbot-nginx
```

### 2. Preparar BASE DE DATOS

#### PostgreSQL Setup
```bash
# Conectarse a PostgreSQL
sudo -u postgres psql

# Crear usuario
CREATE USER inspectify_user WITH PASSWORD 'strong-password-here';

# Crear base de datos
CREATE DATABASE inspectify_db OWNER inspectify_user;

# Configurar permisos
ALTER ROLE inspectify_user SET client_encoding TO 'utf8';
ALTER ROLE inspectify_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE inspectify_user SET default_transaction_deferrable TO on;
ALTER ROLE inspectify_user SET default_transaction_level TO 'read committed';

# Salir
\q
```

### 3. Clonar y Configurar el Proyecto

```bash
# Crear usuario para la aplicación (opcional pero recomendado)
sudo useradd -m -s /bin/bash inspectify
sudo su - inspectify

# Clonar repositorio
git clone <tu-repo> /home/inspectify/app
cd /home/inspectify/app

# Crear virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn
```

### 4. Configurar Variables de Entorno

```bash
# Crear archivo .env en producción
nano .env
```

Copiar contenido de `.env.example` y reemplazar valores:
```
SECRET_KEY=<generar-con-django-insecure>
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_NAME=inspectify_db
DATABASE_USER=inspectify_user
DATABASE_PASSWORD=strong-password-here
DATABASE_HOST=localhost
DATABASE_PORT=5432
GEMINI_API_KEY=<tu-api-key>
```

### 5. Generar SECRET_KEY de Django

```bash
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
exit()
```

### 6. Ejecutar Migraciones

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 8. Configurar Gunicorn

Crear archivo de servicio systemd:
```bash
sudo nano /etc/systemd/system/inspectify.service
```

Contenido:
```ini
[Unit]
Description=Inspectify Django Application
After=network.target

[Service]
User=inspectify
Group=www-data
WorkingDirectory=/home/inspectify/app
ExecStart=/home/inspectify/app/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --config /home/inspectify/app/gunicorn_config.py \
    inspectify.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9. Habilitar Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable inspectify.service
sudo systemctl start inspectify.service
sudo systemctl status inspectify.service
```

### 10. Configurar Nginx

Crear archivo de configuración:
```bash
sudo nano /etc/nginx/sites-available/inspectify
```

Contenido:
```nginx
upstream inspectify_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://inspectify_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/inspectify/app/staticfiles/;
    }

    location /media/ {
        alias /home/inspectify/app/media/;
    }
}
```

### 11. Habilitar Sitio en Nginx

```bash
sudo ln -s /etc/nginx/sites-available/inspectify /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 12. SSL/TLS con Let's Encrypt

```bash
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### 13. Configurar Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 14. Configurar Logs

```bash
# Crear directorio de logs
mkdir -p /home/inspectify/logs
nano /etc/systemd/system/inspectify.service
```

Agregar a la sección `[Service]`:
```
StandardOutput=file:/home/inspectify/logs/access.log
StandardError=file:/home/inspectify/logs/error.log
```

### 15. Monitoreo (Opcional)

```bash
# Instalar htop para monitoreo
sudo apt install htop

# Ver estado de Gunicorn
sudo journalctl -u inspectify -f
```

---

## 🔧 Actualizar Configuración de Django

### settings.py ya debe tener:
- ✅ `DEBUG = os.getenv('DEBUG') == 'True'` (False en producción)
- ✅ `SECRET_KEY = os.getenv('SECRET_KEY')`
- ✅ `DATABASES` configurada con PostgreSQL
- ⚠️ `ALLOWED_HOSTS` debe estar actualizado con tus dominios

### Agregar en settings.py para producción:

```python
# Security Settings (agregar al final)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
    }
```

---

## ✅ Checklist Post-Deployment

- [ ] Verificar que el sitio es accesible en HTTPS
- [ ] Verificar panel de admin (`/admin`)
- [ ] Revisar logs de errores: `sudo journalctl -u inspectify -f`
- [ ] Hacer backup de la base de datos
- [ ] Configurar backups automáticos
- [ ] Probartodas las funcionalidades principales
- [ ] Configurar alertas de monitoreo

---

## 📚 Recursos Útiles

- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 🆘 Troubleshooting

### Error: "Connection refused"
```bash
# Verificar si Gunicorn está corriendo
sudo systemctl status inspectify.service
sudo journalctl -u inspectify -f
```

### Error: "No module named 'django'"
```bash
# Asegurarse de activar venv
source /home/inspectify/app/venv/bin/activate
```

### Error: Database connection
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT datname FROM pg_database;"
```

### Static files no se cargan
```bash
# Recolectar static files
python manage.py collectstatic --noinput
# Reiniciar Nginx
sudo systemctl restart nginx
```
