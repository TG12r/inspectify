# Manual de Scrapers de Empleo

Este módulo permite buscar ofertas de empleo en múltiples fuentes de manera unificada y automatizada.

## 🏗 Arquitectura

El sistema se basa en una clase abstracta `JobScraper` que define la interfaz común. Cada fuente (LinkedIn, RemoteOK, etc.) es una implementación de esta clase.

### Estructura de Archivos
- `jobs/scrapers/base.py`: Define la clase base `JobScraper`.
- `jobs/scrapers/linkedin.py`: Scraper para LinkedIn usando Selenium (simula navegador).
- `jobs/scrapers/remoteok.py`: Scraper para RemoteOK usando su API pública.
- `jobs/management/commands/scrape_jobs.py`: Comando de gestión unificado.

## 🚀 Uso Manual

Puedes ejecutar los scrapers desde la línea de comandos:

```bash
# Buscar en todas las fuentes (por defecto: API 510)
python manage.py scrape_jobs --keywords "API 510"

# Buscar solo en LinkedIn
python manage.py scrape_jobs --source linkedin --keywords "NDT Technician" --location "Houston"

# Buscar solo en RemoteOK (menos relevante para este sector, pero útil para management)
python manage.py scrape_jobs --source remoteok --keywords "Project Manager"

# Limitar resultados (por defecto 10)
python manage.py scrape_jobs --limit 5
```

## 🤖 Automatización y Programación

El sistema usa `django-background-tasks` para ejecutar las búsquedas periódicamente.

### Programar una Tarea Diaria
Ejecuta el comando con el flag `--schedule`:

```bash
python manage.py scrape_jobs --schedule --keywords "API 570" --limit 20
```

Esto creará una tarea en la base de datos que se repetirá cada 24 horas.

### Ejecutar el Procesador de Tareas
Para que las tareas programadas se ejecuten, debes tener corriendo este proceso en segundo plano:

```bash
python manage.py process_tasks
```

## 🛠 Agregar Nuevos Scrapers

Para agregar una nueva fuente (ej: Python.org):

1.  Crear `jobs/scrapers/pythonorg.py`.
2.  Heredar de `JobScraper` e implementar el método `search`.
3.  Registrar el nuevo scraper en `jobs/management/commands/scrape_jobs.py`.

```python
# jobs/scrapers/pythonorg.py
from .base import JobScraper

class PythonOrgScraper(JobScraper):
    def search(self, keywords, location, limit=10):
        # Lógica de scraping...
        returnList[Dict]
```

## 📦 Dependencias

Asegúrate de tener instalados los paquetes necesarios:

```bash
pip install selenium webdriver-manager django-background-tasks requests beautifulsoup4
```

- **Selenium**: Necesario para LinkedIn (requiere Chrome instalado).
- **Webdriver Manager**: Gestiona automáticamente el driver de Chrome.
