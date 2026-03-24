import google.generativeai as genai
from django.conf import settings
import logging
import json
import pdfplumber
import docx

logger = logging.getLogger(__name__)

class AIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set.")
            self.model = None
            self.initialized = True
            return

        try:
            # Usando la librería google-generativeai (más estable/antigua)
            genai.configure(api_key=api_key)
            # Probamos con gemini-2.0-flash que aparecía en tu lista
            self.model_name = 'gemini-2.5-flash'
            self.model = genai.GenerativeModel(self.model_name)
            self.initialized = True
            logger.info(f"Gemini AI ({self.model_name}) initialized successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini AI: {e}")
            self.model = None
            self.initialized = True

    def extract_resume_data(self, file):
        """
        Extrae datos del CV subido (PDF/DOCX) usando Gemini AI.
        """
        import time
        if not self.model:
            logger.error("Gemini model not initialized")
            return {}

        # 1. Extraer texto del archivo según su extensión
        extension = file.name.split('.')[-1].lower()
        text = ""
        try:
            if extension == 'pdf':
                with pdfplumber.open(file) as pdf:
                    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            elif extension == 'docx':
                doc = docx.Document(file)
                text = "\n".join([para.text for para in doc.paragraphs])
            else:
                return {}
        except Exception as e:
            logger.error(f"Extraction Error from {extension}: {e}")
            return {}

        if not text.strip():
            return {}

        logger.info(f"Extracting data from {len(text)} chars of text using {self.model_name}")

        # 2. Enviar a Gemini para estructurar en JSON con detalle
        prompt = f"""
        Actúa como experto en RRHH. Extrae la información del CV y devuélvela estrictamente en JSON.
        
        Estructura requerida:
        {{
            "title": "título profesional",
            "summary": "resumen profesional",
            "phone": "teléfono",
            "address": "ubicación",
            "linkedin_url": "url linkedin",
            "experiences": [
                {{
                    "job_title": "puesto",
                    "company": "empresa",
                    "location": "ciudad",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD o null",
                    "is_current": boolean,
                    "description": "responsabilidades"
                }}
            ],
            "education": [
                {{
                    "institution": "institución",
                    "degree": "título",
                    "field_of_study": "campo",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD o null",
                    "description": "detalles"
                }}
            ],
            "skills": [
                {{
                    "name": "habilidad",
                    "level": "Beginner, Intermediate, Advanced, Expert"
                }}
            ]
        }}

        Instrucciones:
        1. JSON puro, sin texto adicional.
        2. Fechas en YYYY-MM-DD (si solo hay año, usa YYYY-01-01).
        3. Dejalo en el idioma original del CV.

        Texto CV:
        {text[:8000]}
        """

        # Intento con reintento simple para esquivar 429
        for attempt in range(2):
            try:
                response = self.model.generate_content(prompt)
                raw_text = response.text.strip()
                
                # Limpiar posibles bloques de código markdown
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[-1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[-1].split("```")[0].strip()
                
                return json.loads(raw_text)
            except Exception as e:
                logger.warning(f"Intento {attempt+1} fallido: {e}")
                if "429" in str(e):
                    time.sleep(2) # Esperar un poco
                    continue
                break
        
        return {}

    def improve_description(self, text: str, job_title: str) -> str:
        if not self.model: return "Error: IA no configurada."
        prompt = f"Mejora esta descripción de experiencia laboral para '{job_title}': {text}"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except: return "Error mejorando texto."

    def improve_education_description(self, text: str, degree: str, institution: str) -> str:
        if not self.model: return "Error: IA no configurada."
        prompt = f"Mejora esta descripción académica para '{degree}' en '{institution}': {text}"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except: return "Error mejorando texto."

    def improve_summary(self, text: str, job_title: str = "Profesional") -> str:
        if not self.model: return "Error: IA no configurada."
        prompt = f"Mejora este resumen profesional para '{job_title}': {text}"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except: return "Error mejorando resumen."

    def improve_skill_description(self, skill_name: str, level: str) -> str:
        if not self.model: return ""
        prompt = f"Describe brevemente cómo demostrar la habilidad '{skill_name}' nivel '{level}'."
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except: return ""

    def analyze_resume(self, resume_text: str) -> dict:
        if not self.model: return {"error": "IA no configurada."}
        prompt = f"Analiza este CV y devuelve fortalezas, debilidades, sugerencias y puntaje 0-100 en JSON: {resume_text[:4000]}"
        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            if "```json" in text_response: text_response = text_response.replace("```json", "").replace("```", "")
            return json.loads(text_response)
        except: return {"error": "Error analizando el CV."}
