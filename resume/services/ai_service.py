
import google.generativeai as genai
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
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to configure Gemini AI: {e}")
            self.model = None

    def improve_description(self, text: str, job_title: str) -> str:
        """
        Rewrites a job description to be more professional and impact-oriented.
        """
        if not self.model:
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
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Generation Error: {e}")
            return f"Error mejorando texto. Intente más tarde."

    def analyze_resume(self, resume_text: str) -> dict:
        """
        Analyzes the full resume text and provides feedback.
        """
        if not self.model:
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
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            # Clean possible markdown code blocks
            if "```json" in text_response:
                text_response = text_response.replace("```json", "").replace("```", "")
            
            return json.loads(text_response)
        except Exception as e:
            logger.error(f"AI Analysis Error: {e}")
            return {"error": "Error analizando el CV."}
