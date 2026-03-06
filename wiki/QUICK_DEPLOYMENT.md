# GUÍA RÁPIDA: Opciones de Deployment

## Opción 1️⃣ - DOCKER (⭐ RECOMENDADO - Más Fácil)

### Pasos rápidos:
```bash
# 1. Actualizar .env
cp .env.example .env
# Editar .env con tus valores

# 2. Ejecutar con Docker
docker-compose up -d

# 3. Crear superusuario
docker-compose exec web python manage.py createsuperuser

# 4. Acceder en https://localhost
```

**Ventajas:**
- ✅ Fácil de reproducir
- ✅ Incluye PostgreSQL, Redis, Nginx automáticamente
- ✅ Escalable
- ✅ Mismo entorno desarrollo/producción

**Requiere:** Docker y Docker Compose instalados

---

## Opción 2️⃣ - VPS MANUAL (Ubuntu + Nginx + Gunicorn)

### Pasos rápidos (Ver DEPLOYMENT.md para detalles):
```bash
# 1. SSH al servidor
ssh root@tu-ip-servidor

# 2. Instalar dependencias
sudo apt update && sudo apt upgrade
sudo apt install -y python3-pip python3-venv postgresql nginx git supervisor

# 3. Clonar proyecto
git clone <tu-repo> /home/inspectify/app
cd /home/inspectify/app

# 4. Setup venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# 5. Configurar .env
cp .env.example .env
nano .env

# 6. Migraciones
python manage.py migrate
python manage.py collectstatic --noinput

# 7. Configurar Gunicorn (systemd)
sudo nano /etc/systemd/system/inspectify.service
# Copiar contenido de DEPLOYMENT.md

# 8. Configurar Nginx
sudo nano /etc/nginx/sites-available/inspectify
# Usar nginx.conf como referencia

# 9. SSL
sudo certbot --nginx -d tudominio.com

# 10. Iniciar
sudo systemctl start inspectify
sudo systemctl restart nginx
```

**Ventajas:**
- ✅ Control total del servidor
- ✅ Flexible
- ✅ Menos overhead

**Requiere:** Servidor Linux (Ubuntu 20.04+), conocimiento de Linux

---

## Opción 3️⃣ - PLATAFORMAS ADMINISTRADAS

### PaaS (Platform-as-a-Service):

#### **Heroku** (Deprecado - Considerar alternativas)
- ❌ Ya no ofrece plan gratuito

#### **Railway.app** ⭐ (Fácil, Económico)
- ✅ Deploy en 5 minutos
- ✅ PostgreSQL incluido
- ✅ Plan gratuito: $5-10/mes

#### **Render** ⭐ (Muy recomendado)
- ✅ Deploy automático desde GitHub
- ✅ PostgreSQL y Redis gratuitos
- ✅ Plan gratuito: ~$7/mes
- [deploy.render.com](https://deploy.render.com)

#### **PythonAnywhere**
- ✅ Específico para Python/Django
- ✅ Inicio fácil
- Plan gratuito limitado

---

## Opción 4️⃣ - CLOUD (AWS, Google Cloud, Azure)

### AWS Lightsail:
```bash
# Servidor dedicado por ~$5/mes
# Documentación: https://docs.aws.amazon.com/lightsail/
```

### Google Cloud Platform:
```bash
# Compute Engine
# Documentación: https://cloud.google.com/compute/docs
```

---

## ✅ CHECKLIST RECOMENDADO

**Elije una opción:**

### SI QUIERES LO MÁS FÁCIL:
→ **Opción 1: Docker Compose**
→ O **Opción 3: Render.app**

### SI TIENES PRESUPUESTO BAJO:
→ **Opción 1: Docker** en servidor $3-5/mes
→ O **Opción 3: Render.app** gratuitamente

### SI QUIERES CONTROL TOTAL:
→ **Opción 2: Manual en VPS** (DigitalOcean, Linode, Vultr)

---

## 📋 ANTES DE PRODUCCIÓN

- [ ] Generar nuevo SECRET_KEY seguro
- [ ] Cambiar DEBUG = False
- [ ] Actualizar ALLOWED_HOSTS
- [ ] Configurar Email (si aplica)
- [ ] Configurar base de datos PostgreSQL
- [ ] Configurar SSL/HTTPS
- [ ] Configurar backups automáticos
- [ ] Probar todas las funcionalidades
- [ ] Configurar monitoreo y alertas

---

## 🆘 ARCHIVOS ÚTILES EN EL PROYECTO

- **DEPLOYMENT.md** - Guía detallada paso a paso
- **docker-compose.yml** - Para deployment con Docker
- **Dockerfile** - Imagen Docker del proyecto
- **.env.example** - Variables de entorno necesarias
- **gunicorn_config.py** - Configuración de Gunicorn
- **nginx.conf** - Configuración de Nginx
- **supervisor.conf** - Configuración de Supervisor (alternativa a systemd)
- **backup_db.sh** - Script de backup de base de datos
- **restore_db.sh** - Script de restauración

---

## 🚀 DEPLOY EN 5 MINUTOS (Opción Más Rápida)

### Usando Render.app:

1. Ir a [render.com](https://render.com)
2. Conectar GitHub
3. Crear "New Web Service"
4. Seleccionar repositorio
5. Captura:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn inspectify.wsgi:application`
6. Agregar variables de entorno desde `.env.example`
7. Conectar PostgreSQL Render
8. Deploy ✅

---

## 📞 SOPORTE

Si necesitas ayuda:
```bash
# Ver logs
docker-compose logs web

# O en VPS Linux
sudo journalctl -u inspectify -f
```

Cualquier error, consulta DEPLOYMENT.md o contacta al equipo de DevOps.
