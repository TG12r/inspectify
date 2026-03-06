# 🚀 DEPLOY EN VPS - GUÍA RÁPIDA

## ⚡ PASOS (15 MINUTOS)

### PASO 1: Preparar el Script

```bash
# En tu computadora, ir a la carpeta del proyecto
cd c:\inspectify

# Copiar el script a la VPS
scp deploy_vps.sh usuario@tu-ip-vps:/home/usuario/
```

### PASO 2: Conectar a la VPS

```bash
# SSH a tu VPS
ssh usuario@tu-ip-vps

# Cambiar a root (si es necesario)
sudo su -

# O usa key SSH si la tienes configurada
ssh -i tu-key.pem ubuntu@tu-ip-vps
```

### PASO 3: Ejecutar el Script

```bash
# Hacer el script ejecutable
chmod +x ~/deploy_vps.sh

# Ejecutar con tu dominio y repositorio Git
bash ~/deploy_vps.sh tudominio.com https://github.com/tuusuario/inspectify.git
```

⏳ **El script hace TODO automáticamente (15-20 minutos):**
- ✅ Actualizar sistema
- ✅ Instalar PostgreSQL, Nginx, Python
- ✅ Clonar tu proyecto
- ✅ Crear venv + instalar dependencias
- ✅ Configurar database
- ✅ Ejecutar migraciones
- ✅ Recolectar static files
- ✅ Configurar Gunicorn
- ✅ Configurar Nginx
- ✅ Instalar SSL/HTTPS con Certbot
- ✅ Configurar firewall
- ✅ Configurar backup automático (diario)

### PASO 4: Crear Superusuario

El script te preguntará durante la ejecución por:
- Username
- Email
- Password

### PASO 5: ¡Listo! 🎉

Al finalizar verás:
```
📍 URL: https://tudominio.com
🔐 Admin: https://tudominio.com/admin
```

---

## 🔑 CREDENCIALES GENERADAS

El script genera automáticamente:
- ✅ **SECRET_KEY** - Contraseña de Django
- ✅ **Database Password** - Contraseña de PostgreSQL
- ✅ **DB User** - Usuario de la base de datos

**⚠️ GUARDAR EN LUGAR SEGURO** (aparecen en la consola al final)

---

## 📋 REQUISITOS

### De tu VPS:
- [ ] IP / Hostname
- [ ] Usuario + contraseña SSH (o key SSH)
- [ ] Root access (o usuario con sudo)
- [ ] Ubuntu 20.04 o 22.04 (recomendado)
- [ ] Mínimo 1GB RAM, 20GB disco

### De tu Proyecto:
- [ ] Repositorio Git público (o privado con permisos)
- [ ] Dominio disponible (apuntando a tu IP)

### De tu Dominio:
- [ ] A Record → IP de tu VPS
- [ ] Ejemplo:
  ```
  tudominio.com    A    123.456.789.0
  www.tudominio.com CNAME tudominio.com
  ```

---

## ⚙️ DESPUÉS DEL DEPLOY

### 1. Actualizar API Key de Gemini

```bash
# SSH a la VPS
ssh usuario@tu-ip-vps

# Editar .env
nano /home/inspectify/app/.env

# Buscar "GEMINI_API_KEY" y actualizar
# Guardar: Ctrl+X, Y, Enter

# Reiniciar la app
sudo systemctl restart inspectify
```

### 2. Verificar que todo funciona

```bash
# En la VPS
curl -I https://tudominio.com
# Debe devolver: HTTP/2 200

# Ver logs
tail -f /home/inspectify/logs/error.log

# Ver estado de la app
sudo systemctl status inspectify
```

### 3. Acceder a la Admin

- Ir a: `https://tudominio.com/admin`
- Login con las credenciales que creaste
- Verificar que todo está bien

---

## 🐛 TROUBLESHOOTING

### Error: "Connection refused"
```bash
# Ver si la app está corriendo
sudo systemctl status inspectify

# Si no está, reiniciarla
sudo systemctl restart inspectify

# Ver por qué falló
sudo journalctl -u inspectify -n 50
```

### Error: "Bad request" o "Disallowed host"
```bash
# Editar .env
nano /home/inspectify/app/.env

# Verificar ALLOWED_HOSTS:
# ALLOWED_HOSTS=tudominio.com,www.tudominio.com,localhost,127.0.0.1

# Reiniciar
sudo systemctl restart inspectify
```

### Static files no se ven
```bash
# Recolectar static files
cd /home/inspectify/app
/home/inspectify/app/venv/bin/python manage.py collectstatic --noinput

# Reiniciar Nginx
sudo systemctl restart nginx
```

### SSL no funciona
```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificado
sudo certbot renew --dry-run

# Nginx debería renovarlos automáticamente cada día
```

---

## 📊 COMANDOS ÚTILES

```bash
# Ver estado de aplicación
sudo systemctl status inspectify

# Reiniciar aplicación
sudo systemctl restart inspectify

# Ver logs de la app en tiempo real
sudo journalctl -u inspectify -f

# Ver logs de Nginx
tail -f /var/log/nginx/error.log

# Ver logs de acceso
tail -f /var/log/nginx/access.log

# Ejecutar comando Django
/home/inspectify/app/venv/bin/python /home/inspectify/app/manage.py <comando>

# Crear nuevo superusuario después
sudo -u inspectify /home/inspectify/app/venv/bin/python /home/inspectify/app/manage.py createsuperuser

# Ver estado de PostgreSQL
sudo systemctl status postgresql

# Backup manual
/home/inspectify/app/backup_db.sh

# Listar backups
ls -lh /home/inspectify/backups/
```

---

## 🔒 SEGURIDAD

✅ El script configura automáticamente:
- Firewall bloqueado (solo puertos 22, 80, 443)
- HTTPS obligatorio (HTTP redirige a HTTPS)
- Headers de seguridad
- CSRF protection
- XSS protection
- Rate limiting

⚠️ **TODAVÍA DEBES:**
1. Cambiar contraseña SSH por key SSH
2. Deshabilitar root login
3. Configurar fail2ban (opcional)
4. Actualizar GEMINI_API_KEY en .env

---

## 📱 MONITOREO

Después de deploy, comprobar que todo está ok:

```bash
# Verificar que app responde
curl -I https://tudominio.com
# Debe retornar: HTTP/2 200

# Verificar que admin funciona
curl -I https://tudominio.com/admin
# Debe retornar: HTTP/2 302 (redirect a login)

# Ver recursos usados
htop

# Ver tamaño de la db
du -sh /home/inspectify/app/

# Ver espacio en disco
df -h
```

---

## 🆘 Si algo sale mal

1. **Leer la salida del script** - Dice exactamente qué falló
2. **Ver logs:** `sudo journalctl -u inspectify -n 100`
3. **Verificar .env:** `cat /home/inspectify/app/.env`
4. **Verificar permisos:** `ls -la /home/inspectify/app/`
5. **Reiniciar todo:**
   ```bash
   sudo systemctl restart inspectify
   sudo systemctl restart nginx
   sudo systemctl restart postgresql
   ```

---

## ✅ CHECKLIST FINAL

Después de deploy, verificar:

- [ ] Sitio accesible en https://tudominio.com ✅
- [ ] Admin funciona en /admin ✅
- [ ] No hay errores en logs ✅
- [ ] Static files se cargan (CSS, JS) ✅
- [ ] GEMINI_API_KEY actualizada ✅
- [ ] SSL está instalado (candado verde) ✅
- [ ] Backup automático configurado ✅
- [ ] Firewall está habilitado ✅

---

¿Todo listo? **¡A PRODUCCIÓN! 🚀**

Dudas: Ver logs o contactar al equipo DevOps.
