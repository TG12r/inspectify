#!/bin/bash

# Script de Restauración de Base de Datos
# Uso: ./restore_db.sh backup_file.sql

if [ -z "$1" ]; then
    echo "Uso: $0 <archivo_backup.sql>"
    exit 1
fi

BACKUP_FILE=$1
DB_NAME="inspectify_db"
DB_USER="inspectify_user"
DB_HOST="localhost"

# Descomprimir si es necesario
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | psql -h $DB_HOST -U $DB_USER $DB_NAME
else
    psql -h $DB_HOST -U $DB_USER $DB_NAME < $BACKUP_FILE
fi

echo "Restauración completada desde: $BACKUP_FILE"
