import re
from ..models import Resume

def calculate_resume_health(resume: Resume):
    """
    Analyzes the resume and returns a health score (0-100),
    a list of checks (passed/failed), and suggestions.
    """
    score = 0
    checks = []
    suggestions = []
    
    # --- 1. COMPLETENESS (30%) ---
    completeness_score = 0
    
    # Header / Contact Info
    if resume.title:
        completeness_score += 5
        checks.append({'label': 'Título Profesional', 'status': True})
    else:
        checks.append({'label': 'Título Profesional', 'status': False})
        suggestions.append("Agrega un título profesional (ej: 'Senior Python Developer')")

    if resume.summary:
        completeness_score += 5
        checks.append({'label': 'Resumen Profesional', 'status': True})
    else:
        checks.append({'label': 'Resumen Profesional', 'status': False})
        suggestions.append("Tu CV necesita un resumen profesional que destaque tu valor.")

    if resume.linkedin_url:
        completeness_score += 5
        checks.append({'label': 'Enlace a LinkedIn', 'status': True})
    else:
        checks.append({'label': 'Enlace a LinkedIn', 'status': False})
        suggestions.append("Incluye tu perfil de LinkedIn para mayor credibilidad.")

    # Relations
    has_experience = resume.experiences.exists()
    has_education = resume.education.exists()
    has_skills = resume.skills.exists()
    
    if has_experience:
        completeness_score += 10
        checks.append({'label': 'Experiencia Laboral', 'status': True})
    else:
        checks.append({'label': 'Experiencia Laboral', 'status': False})
        suggestions.append("Agrega al menos una experiencia laboral.")
        
    if has_education:
        completeness_score += 5
        checks.append({'label': 'Educación', 'status': True})
    else:
        checks.append({'label': 'Educación', 'status': False})
        suggestions.append("Incluye tu formación académica.")

    # Score cap for completeness section
    score += completeness_score
    
    # --- 2. IMPACT & CONTENT (40%) ---
    impact_score = 0
    
    # Action Verbs (Spanish)
    action_verbs = [
        'lideré', 'desarrollé', 'gestioné', 'implementé', 'diseñé', 
        'creé', 'aumenté', 'reduje', 'optimicé', 'logré', 'coordiné',
        'supervisé', 'lancé', 'negocié', 'resolví'
    ]
    
    # Metrics Regex (numbers, %, $)
    metrics_pattern = re.compile(r'(\d+%|\$\d+|\d+\s+millones|\d+\s+usuarios|\d+\s+equipos)', re.IGNORECASE)
    
    experiences = resume.experiences.all()
    if experiences:
        # Check descriptions
        total_exp = len(experiences)
        with_metrics = 0
        with_action_verbs = 0
        
        for exp in experiences:
            desc_lower = exp.description.lower()
            
            # Check for action verbs
            if any(verb in desc_lower for verb in action_verbs):
                with_action_verbs += 1
                
            # Check for metrics
            if metrics_pattern.search(exp.description):
                with_metrics += 1
        
        # Scoring logic for Experience content
        if with_action_verbs >= 1:
            impact_score += 20
            checks.append({'label': 'Uso de Verbos de Acción', 'status': True})
        else:
            checks.append({'label': 'Uso de Verbos de Acción', 'status': False})
            suggestions.append("Usa verbos fuertes al inicio de tus puntos (ej: Lideré, Creé, Optimicé).")
            
        if with_metrics >= 1:
            impact_score += 20
            checks.append({'label': 'Logros Cuantificables', 'status': True})
        else:
            checks.append({'label': 'Logros Cuantificables', 'status': False})
            suggestions.append("Incluye números o porcentajes en tus experiencias (ej: 'Aumenté ventas en 20%').")

    else:
        # Penalty if no experience to analyze
        pass
        
    score += impact_score
    
    # --- 3. FORMAT & STRUCTURE (30%) ---
    format_score = 0
    
    # Length Check (approx words)
    # Simple word count of summary + experience descriptions
    total_words = 0
    if resume.summary:
        total_words += len(resume.summary.split())
    
    for exp in experiences:
         total_words += len(exp.description.split())
         
    if 100 <= total_words <= 800:
        format_score += 15
        checks.append({'label': 'Longitud Adecuada', 'status': True})
    elif total_words < 100:
        checks.append({'label': 'Longitud Adecuada', 'status': False})
        suggestions.append("Tu CV parece muy corto. Intenta detallar más tus responsabilidades.")
    else:
        checks.append({'label': 'Longitud Adecuada', 'status': False})
        suggestions.append("Tu CV podría ser demasiado largo. Intenta ser más conciso (apunta a 1 página).")
        
    # Bullet points usage (heuristic: checks for newlines or bullet chars)
    uses_bullets = False
    for exp in experiences:
        if '\n' in exp.description or '•' in exp.description or '-' in exp.description:
            uses_bullets = True
            break
    
    if uses_bullets:
        format_score += 15
        checks.append({'label': 'Uso de Listas', 'status': True})
    else:
        checks.append({'label': 'Uso de Listas', 'status': False})
        suggestions.append("Usa listas (bullet points) en tus experiencias para mejorar la legibilidad.")
        
    score += format_score
    
    # Normalize score cap to 100 just in case
    score = min(score, 100)
    
    # Determine Health Level
    level = 'Bajo'
    color = 'red'
    if score >= 80:
        level = 'Excelente'
        color = 'emerald'
    elif score >= 50:
        level = 'Bueno'
        color = 'amber'
        
    return {
        'score': score,
        'level': level,
        'color': color,
        'checks': checks,
        'suggestions': suggestions
    }
