# 🚀 INSPECTIFY - DEPLOYMENT CHECKLIST

## Pre-Deployment Security Checklist

### 1. Django Settings
- [ ] `DEBUG = False` en producción (verificar .env)
- [ ] `SECRET_KEY` es único y seguro (no el que viene por defecto)
- [ ] `ALLOWED_HOSTS` está configurado correctamente
- [ ] `CSRF_TRUSTED_ORIGINS` si aplica
- [ ] CORS está restringido si tienes APIs

### 2. Database
- [ ] PostgreSQL está instalado y corriendo
- [ ] Base de datos creada
- [ ] Usuario de BD con contraseña fuerte
- [ ] Migrations ejecutadas: `python manage.py migrate`
- [ ] Backups configurados
- [ ] Credenciales en .env (NO en settings.py)

### 3. Static Files & Media
- [ ] Static files recolectados: `python manage.py collectstatic`
- [ ] STATIC_ROOT configurado
- [ ] MEDIA_ROOT configurado 
- [ ] Permisos de carpeta correctos (755)
- [ ] CDN configurado (opcional pero recomendado)

### 4. Web Server
- [ ] Gunicorn instalado
- [ ] gunicorn_config.py configurado
- [ ] Número de workers calculado: (CPU cores * 2) + 1
- [ ] Systemd service creado y habilitado
- [ ] Logs configurados

### 5. Reverse Proxy (Nginx)
- [ ] Nginx configurado
- [ ] Virtual host/server block creado
- [ ] Proxy_pass dirigido a Gunicorn (127.0.0.1:8000)
- [ ] Gzip compression habilitado
- [ ] Rate limiting configurado
- [ ] Nginx testado: `sudo nginx -t`

### 6. HTTPS/SSL
- [ ] Certificado SSL instalado
- [ ] Let's Encrypt renewal automático configurado
- [ ] HTTP redirige a HTTPS
- [ ] HSTS headers configurados
- [ ] TLS 1.2+ configurado

### 7. Firewall & Network
- [ ] UFW/Firewall habilitado
- [ ] Puerto 22 (SSH) permitido
- [ ] Puerto 80 (HTTP) permitido
- [ ] Puerto 443 (HTTPS) permitido
- [ ] Otros puertos bloqueados
- [ ] No exponer directamente puerto 8000 de Gunicorn

### 8. Environment Variables
- [ ] Archivo `.env` existe y tiene permisos 600
- [ ] NO está en git (verificar .gitignore)
- [ ] TODAS las variables requeridas están definidas
- [ ] No hay valores por defecto inseguros

### 9. Logging & Monitoring
- [ ] Directorio de logs creado
- [ ] Logs de Django configurados
- [ ] Logs de Nginx configurados
- [ ] Logs de Gunicorn configurados
- [ ] Log rotation configurado (logrotate)
- [ ] Monitoreo de errores (Sentry, etc.)

### 10. Application Health
- [ ] Ejecutar: `python manage.py check`
- [ ] No hay advertencias de seguridad
- [ ] Crear superusuario: `python manage.py createsuperuser`
- [ ] Acceder a /admin
- [ ] Probar login functional
- [ ] Probar funcionalidades críticas

### 11. Performance & Optimization
- [ ] Database queries optimizadas (select_related, prefetch_related)
- [ ] Cache configurado (Redis)
- [ ] Compresión GZIP habilitada
- [ ] Minificación de CSS/JS
- [ ] Imágenes optimizadas
- [ ] CDN para assets estáticos

### 12. Backups & Disaster Recovery
- [ ] Script de backup de BD creado
- [ ] Backup automático programado (cron job)
- [ ] Prueba de restauración funciona
- [ ] Backups almacenados fuera del servidor
- [ ] Retención de backups: mínimo 30 días
- [ ] Plan de recuperación documentado

### 13. Email (si aplica)
- [ ] Email backend configurado
- [ ] SMTP credenciales en .env
- [ ] Test de envío de email
- [ ] Sender address válido

### 14. Third-party Services
- [ ] API keys en .env (NO en código)
- [ ] Rate limits considerados
- [ ] Error handling para fallos de API

### 15. Git & Deployment
- [ ] Código commiteado
- [ ] `.env` no está en git
- [ ] `__pycache__` no está en git
- [ ] `db.sqlite3` no está en git (si usas SQLite)
- [ ] `venv/` no está en git

### 16. Docker (si usas)
- [ ] Dockerfile creado correctamente
- [ ] docker-compose.yml configurado
- [ ] Volúmenes para datos persistentes
- [ ] Networks correctamente configuradas
- [ ] Healthchecks configurados

### 17. Documentación
- [ ] README con instrucciones de deployment
- [ ] DEPLOYMENT.md completo
- [ ] Variables de entorno documentadas
- [ ] Procedimientos de troubleshooting documentados

---

## Deployment Steps

### Deploy Manual (VPS):
```bash
1. SSH al servidor
2. Clonar código
3. Crear venv e instalar dependencias
4. Configurar .env
5. Ejecutar migraciones
6. Recolectar static files
7. Configurar Gunicorn + systemd
8. Configurar Nginx
9. Instalar SSL
10. Reiniciar servicios
```

### Deploy Docker:
```bash
1. docker-compose build
2. docker-compose up -d
3. docker-compose exec web python manage.py migrate
4. docker-compose exec web python manage.py createsuperuser
```

---

## Post-Deployment

- [ ] Verificar site está accesible
- [ ] Verificar HTTPS funciona
- [ ] Verificar panel admin `/admin`
- [ ] Revisar logs de errores
- [ ] Test de las principales funcionalidades
- [ ] Verificar rendimiento
- [ ] Configurar alertas de monitoreo
- [ ] Comunicar URL a stakeholders

---

## Monitoreo Continuo

```bash
# Ver logs en tiempo real
docker-compose logs -f web

# O en servidor Linux
sudo journalctl -u inspectify -f

# Chequear salud de aplicación
curl https://tudominio.com/health/

# Monitor de recursos
htop  # o: docker stats
```

---

## En Caso de Emergencia

```bash
# Reiniciar aplicación
docker-compose restart web
# O
sudo systemctl restart inspectify

# Ver últimos errores
docker-compose logs --tail 100 web

# Restaurar base de datos desde backup
./restore_db.sh backup_file.sql.gz
```

---

**Última revisión:** 2025-03-05  
**Mantenedor:** DevOps Team
