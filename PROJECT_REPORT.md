# Reporte de Definición de Proyecto: Inspectify

## 1. Visión Ejecutiva
**Inspectify** se define como una plataforma integral diseñada para centralizar el desarrollo profesional y técnico en la industria. Su propuesta de valor única radica en la convergencia de tres pilares fundamentales:
1.  **Repositorio Técnico Especializado:** Acceso a documentación, normas y procedimientos técnicos.
2.  **Mercado Laboral Inteligente (Bolsa de Trabajo):** Agregación automática de ofertas laborales del sector.
3.  **Desarrollo de Carrera Asistido por IA (CV Builder):** Herramienta avanzada para la creación y optimización de currículums.

---

## 2. Arquitectura Tecnológica y Stack

### Decisión Estratégica: Python + Django
Para garantizar la escalabilidad, mantenimiento y capacidad de expansión futura, se ha seleccionado el ecosistema **Python** sobre alternativas como PHP (Laravel) o Go.

*   **¿Por qué Python?**
    *   **Dominio en IA:** Crítico para el módulo de *CV Builder*, donde integraremos modelos de lenguaje (LLMs) para sugerencias de redacción y análisis de perfiles.
    *   **Liderazgo en Scraping:** Bibliotecas como `Scrapy` y `Selenium` son el estándar de la industria para construir el motor de agregación de la *Bolsa de Trabajo*.
    *   **Velocidad de Desarrollo:** Django permite iterar rápidamente el MVP gracias a su robusto ORM y panel de administración integrado.

### Componentes Clave
*   **Backend:** Framework Django (Seguridad, Gestión de Usuarios, ORM).
*   **Base de Datos:** PostgreSQL (Soporte nativo para búsquedas complejas y JSON).
*   **Frontend:** Híbrido. Django Templates para SEO (Portal Público) + React/Alpine.js para interactividad (Constructor de CV).
*   **Infraestructura Asíncrona:** Celery + Redis (Manejo de tareas en segundo plano como scraping y generación de PDFs).

---

## 3. Módulos Funcionales

### A. Bolsa de Trabajo (Job Board) & Agregador
*   **Motor de Scraping:** Crawler automatizado que busca ofertas en portales externos y las centraliza.
*   **Normalización:** Algoritmos para estandarizar títulos y salarios.
*   **Postulación Rápida:** Flujo simplificado para usuarios registrados.

### B. Repositorio Técnico (Knowledge Base)
*   **CMS Documental:** Sistema de gestión para artículos técnicos, normas (API, ASME, etc.) y procedimientos.
*   **Búsqueda Semántica:** Motor de búsqueda capaz de entender el contexto técnico, no solo palabras clave.

### C. Constructor de Currículum con IA (Resume Builder)
*   **Asistente de Redacción:** Sugerencias inteligentes para describir logros y responsabilidades basadas en el rol.
*   **Análisis ATS:** Verificación automática de compatibilidad con sistemas de seguimiento de candidatos.
*   **Exportación Profesional:** Generación de documentos PDF de alta calidad tipográfica.

### D. Gestión de Usuarios y Roles
*   **Profesional:** Acceso a repositorio, bolsa de trabajo y constructor de CV.
*   **Reclutador:** Publicación de ofertas premium y búsqueda de talento.
*   **Administrador:** Gestión global del sistema, contenidos y métricas.

---

## 4. Plan de Implementación (Roadmap MVP)

### Fase 1: Cimientos (Semana 1)
*   Configuración del entorno de desarrollo y repositorio.
*   Diseño de base de datos y modelos núcleo (`User`, `Profile`).

### Fase 2: Motor de Datos (Semana 2)
*   Implementación del módulo de **Bolsa de Trabajo**.
*   Desarrollo de scripts de scraping iniciales para poblar la base de datos.

### Fase 3: Gestión de Conocimiento (Semana 3)
*   Desarrollo del **Repositorio Técnico**.
*   Sistema de carga y visualización de documentos.

### Fase 4: Inteligencia de Usuario (Semana 4)
*   Lanzamiento Beta del **Constructor de CV**.
*   Integración básica de IA para mejora de perfiles.

---

Este informe sirve como documento maestro para el inicio del desarrollo del proyecto **Inspectify**.
