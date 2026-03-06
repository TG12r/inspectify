#!/bin/bash

# Script de Backup de Base de Datos PostgreSQL
# Uso: ./backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/inspectify/backups"
DB_NAME="inspectify_db"
DB_USER="inspectify_user"
DB_HOST="localhost"

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# Realizar dump de la base de datos
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > $BACKUP_DIR/inspectify_db_$DATE.sql

# Comprimir el archivo
gzip $BACKUP_DIR/inspectify_db_$DATE.sql

# Eliminar backups más antiguos de 30 días
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete

echo "Backup completado: $BACKUP_DIR/inspectify_db_$DATE.sql.gz"

# Hacer backup de archivos importantes
tar -czf $BACKUP_DIR/inspectify_media_$DATE.tar.gz /home/inspectify/app/media/

# Eliminar archivos media backup más antiguos de 30 días
find $BACKUP_DIR -type f -name "inspectify_media_*.tar.gz" -mtime +30 -delete

echo "Media backup completado: $BACKUP_DIR/inspectify_media_$DATE.tar.gz"
