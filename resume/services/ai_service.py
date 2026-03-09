    def extract_resume_data(self, file):
        """
        Extrae datos del CV subido (PDF/DOCX). Aquí va la lógica real de extracción con IA o librerías.
        Por ahora, retorna un mock de ejemplo.
        """
        # TODO: Implementar extracción real (pdfplumber, python-docx, IA, etc)
        # file es un UploadedFile de Django
        return {
            'title': 'Ejemplo: Ingeniero de Software',
            'summary': 'Profesional con experiencia en desarrollo web y aplicaciones.',
            'phone': '+34 600 123 456',
            'address': 'Madrid, España',
            'linkedin_url': 'https://linkedin.com/in/ejemplo',
            'experiences': [
                {'job_title': 'Desarrollador', 'company': 'Empresa X', 'location': 'Madrid', 'start_date': '2020-01-01', 'end_date': '2022-01-01', 'is_current': False, 'description': 'Desarrollé aplicaciones web.'}
            ],
            'education': [
                {'institution': 'Universidad Y', 'degree': 'Ingeniería Informática', 'field_of_study': 'Informática', 'start_date': '2015-09-01', 'end_date': '2019-06-30', 'description': 'Graduado con honores.'}
            ],
            'skills': [
                {'name': 'Python', 'level': 'Avanzado'}
            ]
        }

import google.genai as genai
from django.conf import settings
import logging
import json

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
            self.client = None
            self.initialized = True
            return

        try:
            # Nueva API de google.genai
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-2.5-flash-lite'
            self.initialized = True
            logger.info("Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini AI: {e}")
            self.client = None
            self.initialized = True

    def improve_description(self, text: str, job_title: str) -> str:
        """
        Rewrites a job description to be more professional and impact-oriented.
        """
        if not self.client:
            return "Error: Servicio de IA no configurado."

        if not text:
            return ""
            
        if len(text) < 10:
            return "Descripción muy corta para mejorar."

        prompt = f"""
        Actúa como un experto redactor de CVs. Reescribe la siguiente experiencia laboral para el rol de "{job_title}" para que suene más profesional e impactante.
        
        Reglas:
        1. Usa PRIMERA PERSONA (ej: "Lideré", "Desarrollé", "Gestioné").
        2. Enfócate en LOGROS y RESPONSABILIDADES asumidas por el candidato.
        3. NO escribas como si fuera una oferta de trabajo (ej: "Se busca...", "Deberá...").
        4. Usa verbos de acción fuertes.
        5. Cuantifica resultados donde sea posible (o usa [X]%).
        6. Mantenlo conciso (menos de 150 palabras).
        
        Responde SOLO con el texto reescrito en español.

        Descripción Original:
        {text}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Generation Error: {e}")
            return f"Error mejorando texto. Intente más tarde."

    def improve_education_description(self, text: str, degree: str, institution: str) -> str:
        """
        Improves education/training description to highlight achievements and skills gained.
        """
        if not self.client:
            return "Error: Servicio de IA no configurado."

        if not text:
            return ""
            
        if len(text) < 10:
            return "Descripción muy corta para mejorar."

        prompt = f"""
        Actúa como un experto redactor de CVs. Mejora la siguiente descripción de formación académica para el grado "{degree}" en "{institution}".
        
        Reglas:
        1. Destaca LOGROS académicos y PROYECTOS relevantes.
        2. Menciona HABILIDADES adquiridas si es relevante.
        3. Usa TERCERA PERSONA O PASIVA si es necesario.
        4. Sé conciso (menos de 100 palabras).
        5. Mantén un tono académico pero profesional.
        
        Responde SOLO con el texto mejorado en español.

        Descripción Original:
        {text}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Generation Error: {e}")
            return f"Error mejorando texto. Intente más tarde."

    def improve_summary(self, text: str, job_title: str = "Profesional") -> str:
        """
        Improves professional summary to be concise and impactful.
        """
        if not self.client:
            return "Error: Servicio de IA no configurado."

        if not text:
            return ""
            
        if len(text) < 10:
            return "Resumen muy corto para mejorar."

        prompt = f"""
        Actúa como un experto redactor de CVs. Mejora el siguiente RESUMEN PROFESIONAL para un "{job_title}".
        
        Reglas:
        1. MÁXIMO 3-4 líneas (50-80 palabras).
        2. Destaca: EXPERIENCIA + FORTALEZAS + VALOR ÚNICO.
        3. Usa PRIMERA PERSONA y verbos activos.
        4. Sé específico, no genérico.
        5. Oriéntalo a resultados e impacto.
        
        Responde SOLO con el resumen mejorado en español.

        Resumen Original:
        {text}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Generation Error: {e}")
            return f"Error mejorando texto. Intente más tarde."

    def improve_skill_description(self, skill_name: str, level: str) -> str:
        """
        Generates a brief description of how to demonstrate a skill.
        """
        if not self.client:
            return "Error: Servicio de IA no configurado."

        prompt = f"""
        Actúa como un experto en recursos humanos. Crea UNA LÍNEA corta (máximo 15 palabras) que describa cómo demostrar competencia en "{skill_name}" a nivel "{level}".
        
        Usa lenguaje profesional y orientado a resultados.
        Responde SOLO con esa descripción.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Generation Error: {e}")
            return ""

    def analyze_resume(self, resume_text: str) -> dict:
        """
        Analyzes the full resume text and provides feedback.
        """
        if not self.client:
            return {"error": "Servicio de IA no configurado."}

        prompt = f"""
        Analiza el siguiente texto de un currículum y proporciona 3 mejoras específicas en formato JSON con la siguiente estructura:
        {{
            "strengths": ["fuerte 1", "fuerte 2"],
            "weaknesses": ["debilidad 1", "debilidad 2"],
            "suggestions": ["sugerencia 1", "sugerencia 2"],
            "score": <0-100 integer estimated score>
        }}
        
        Texto del CV:
        {resume_text[:4000]} 
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text_response = response.text.strip()
            # Clean possible markdown code blocks
            if "```json" in text_response:
                text_response = text_response.replace("```json", "").replace("```", "")
            
            return json.loads(text_response)
        except Exception as e:
            logger.error(f"AI Analysis Error: {e}")
            return {"error": "Error analizando el CV."}
