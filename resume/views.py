from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.cache import cache
import json
from datetime import date

from .models import Resume, Experience, Education, Skill
from .forms import ResumeForm, ExperienceForm, EducationForm, SkillForm
from .services.ai_service import AIService
from .services.health_service import calculate_resume_health
from core.models import UserProfile
from core.forms import UserProfileForm


@login_required
def resume_edit(request):
    resume, created = Resume.objects.get_or_create(user=request.user)
    profile, created_profile = UserProfile.objects.get_or_create(user=request.user)

    # Lazy sync: If profile is empty/new but resume has data, copy resume data to profile
    if created_profile or not profile.title:
        if resume.title: profile.title = resume.title
        if resume.phone: profile.phone = resume.phone
        if resume.address: profile.location = resume.address # address maps to location
        if resume.linkedin_url: profile.linkedin_url = resume.linkedin_url
        if resume.summary: profile.bio = resume.summary # summary maps to bio (opcional, pero bueno para consistencia)
        profile.save()

    if request.method == 'POST':
        # 1. ¿Viene un archivo para extraer con IA?
        cv_file = request.FILES.get('cv_file')
        if cv_file:
            # --- PROTECCIÓN DE COSTOS / LÍMITE DE USO ---
            cache_key = f"ai_extract_limit_{request.user.id}"
            usage_count = cache.get(cache_key, 0)
            
            if usage_count >= 3: # Límite de 3 extracciones al día por usuario
                messages.error(request, "Has alcanzado el límite diario de extracciones con IA (3). Inténtalo de nuevo mañana.")
                return redirect('resume_edit')
            
            # --------------------------------------------
            ai_service = AIService()
            extracted_data = ai_service.extract_resume_data(cv_file)
            
            if extracted_data:
                # Incrementar contador de uso (clack por 24 horas)
                cache.set(cache_key, usage_count + 1, 86400)
                
                request.session['extracted_resume_data'] = extracted_data
                return redirect('resume_compare')
            else:
                messages.error(request, "No se pudo extraer información del archivo. Asegúrate de que sea un PDF o DOCX legible.")
                return redirect('resume_edit')

        # Prioridad 2: Guardado normal del perfil y campos del resume
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()

            # Sync back: Update Resume model with Profile data to keep Preview working
            resume.title = profile.title
            resume.phone = profile.phone
            resume.address = profile.location
            resume.linkedin_url = profile.linkedin_url
            resume.save()

            messages.success(request, 'Tu currículum y perfil han sido actualizados exitosamente.')
            return redirect('resume_edit')
    else:
        form = ResumeForm(instance=resume)
        profile_form = UserProfileForm(instance=profile)

    # --- INFORMACIÓN DE LÍMITES IA ---
    cache_key = f"ai_extract_limit_{request.user.id}"
    usage_count = cache.get(cache_key, 0)
    remaining_ai_uses = max(0, 3 - usage_count)
    # ---------------------------------

    # Get additional context if needed
    resume_health = calculate_resume_health(resume) # Reverted to original calculation, as the instruction's snippet seemed to remove it unintentionally.

    context = {
        'form': form,
        'profile_form': profile_form,
        'resume': resume,
        'experiences': resume.experiences.all(),
        'educations': resume.education.all(),
        'skills': resume.skills.all(),
        'resume_health': resume_health,
        'remaining_ai_uses': remaining_ai_uses,
    }
    return render(request, 'resume/resume_edit.html', context)


# Vista para comparar campos actuales vs extraídos

@login_required
def resume_compare(request):
    resume = Resume.objects.get(user=request.user)
    extracted_data = request.session.get('extracted_resume_data')
    if not extracted_data:
        messages.error(request, 'No se encontraron datos extraídos. Sube un CV primero.')
        return redirect('resume_edit')

    # Configuración de campos para la comparación
    fields_to_compare = [
        {'key': 'title', 'label': 'Título Profesional'},
        {'key': 'summary', 'label': 'Resumen / Bio'},
        {'key': 'phone', 'label': 'Teléfono'},
        {'key': 'address', 'label': 'Ubicación'},
        {'key': 'linkedin_url', 'label': 'LinkedIn'},
    ]
    
    fields_config = []
    for field in fields_to_compare:
        fields_config.append({
            'key': field['key'],
            'label': field['label'],
            'current': getattr(resume, field['key'], ''),
            'extracted': extracted_data.get(field['key'], '')
        })

    # Preparar experiencias para comparación
    experiences_current = list(resume.experiences.all().values())
    experiences_extracted = extracted_data.get('experiences', [])
    
    # Preparar educación para comparación
    education_current = list(resume.education.all().values())
    education_extracted = extracted_data.get('education', [])

    # Preparar habilidades
    skills_current = list(resume.skills.all().values())
    skills_extracted = extracted_data.get('skills', [])

    if request.method == 'POST':
        selected = request.POST
        # Campos simples
        for field in ['title', 'summary', 'phone', 'address', 'linkedin_url']:
            value = selected.get(field)
            if value is not None:
                setattr(resume, field, value)
        resume.save()

        # Experiencias
        experience_mode = selected.get('experience_mode')
        if experience_mode == 'replace':
            resume.experiences.all().delete()
            for exp in extracted_data.get('experiences', []):
                # Validar fechas básicas o usar null
                s_date = exp.get('start_date') if exp.get('start_date') else None
                e_date = exp.get('end_date') if exp.get('end_date') else None
                resume.experiences.create(
                    job_title=(exp.get('job_title') or 'Sin Título')[:255],
                    company=(exp.get('company') or 'Empresa desconocida')[:255],
                    location=(exp.get('location') or '')[:255],
                    start_date=s_date or '2020-01-01',
                    end_date=e_date,
                    is_current=exp.get('is_current') or False,
                    description=exp.get('description') or ''
                )

        # Educación
        education_mode = selected.get('education_mode')
        if education_mode == 'replace':
            resume.education.all().delete()
            for edu in extracted_data.get('education', []):
                s_date = edu.get('start_date') if edu.get('start_date') else None
                e_date = edu.get('end_date') if edu.get('end_date') else None
                resume.education.create(
                    institution=(edu.get('institution') or 'Institución desconocida')[:255],
                    degree=(edu.get('degree') or 'Título desconocido')[:255],
                    field_of_study=(edu.get('field_of_study') or '')[:255],
                    start_date=s_date or '2015-01-01',
                    end_date=e_date,
                    description=edu.get('description') or ''
                )

        # Habilidades (Siempre añadir las nuevas si no existen o reemplazar según lógica)
        # Por ahora, simplemente las reemplazamos todas si hay datos extraídos
        if extracted_data.get('skills'):
            resume.skills.all().delete()
            for skill in extracted_data.get('skills', []):
                resume.skills.create(
                    name=(skill.get('name', ''))[:255],
                    level=skill.get('level', 'Intermediate')
                )

        # Limpiar datos extraídos de la sesión
        if 'extracted_resume_data' in request.session:
            del request.session['extracted_resume_data']
            
        messages.success(request, 'Currículum actualizado con los datos seleccionados.')
        return redirect('resume_edit')

    context = {
        'resume': resume,
        'extracted_data': extracted_data,
        'fields_config': fields_config,
        'experiences_current': experiences_current,
        'experiences_extracted': experiences_extracted,
        'education_current': education_current,
        'education_extracted': education_extracted,
        'skills_current': skills_current,
        'skills_extracted': skills_extracted,
    }
    return render(request, 'resume/resume_compare.html', context)

@login_required
def resume_preview(request):
    resume = get_object_or_404(Resume, user=request.user)
    context = {
        'resume': resume,
        'experiences': resume.experiences.all(),
        'education': resume.education.all(),
        'skills': resume.skills.all(),
    }
    return render(request, 'resume/resume_preview.html', context)

# --- Experience HTMX Views ---

@login_required
def add_experience(request):
    try:
        if request.method == 'POST':
            form = ExperienceForm(request.POST)
            if form.is_valid():
                experience = form.save(commit=False)
                resume, _ = Resume.objects.get_or_create(user=request.user)
                experience.resume = resume
                experience.save()
                return render(request, 'resume/partials/experience_item.html', {'experience': experience})
        else:
            form = ExperienceForm()
        
        return render(request, 'resume/partials/experience_form.html', {'form': form})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {e}", status=500)

@login_required
def edit_experience(request, pk):
    experience = get_object_or_404(Experience, pk=pk, resume__user=request.user)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            experience = form.save()
            return render(request, 'resume/partials/experience_item.html', {'experience': experience})
    else:
        form = ExperienceForm(instance=experience)
    
    return render(request, 'resume/partials/experience_form.html', {'form': form, 'experience': experience})

@login_required
@require_http_methods(['DELETE'])
def delete_experience(request, pk):
    experience = get_object_or_404(Experience, pk=pk, resume__user=request.user)
    experience.delete()
    return HttpResponse("")

# --- Education HTMX Views ---

@login_required
def add_education(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            resume, _ = Resume.objects.get_or_create(user=request.user)
            education.resume = resume
            education.save()
            return render(request, 'resume/partials/education_item.html', {'education': education})
    else:
        form = EducationForm()
    
    return render(request, 'resume/partials/education_form.html', {'form': form})

@login_required
def edit_education(request, pk):
    education = get_object_or_404(Education, pk=pk, resume__user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            education = form.save()
            return render(request, 'resume/partials/education_item.html', {'education': education})
    else:
        form = EducationForm(instance=education)
    
    return render(request, 'resume/partials/education_form.html', {'form': form, 'education': education})

@login_required
@require_http_methods(['DELETE'])
def delete_education(request, pk):
    education = get_object_or_404(Education, pk=pk, resume__user=request.user)
    education.delete()
    return HttpResponse("")

# --- Skill HTMX Views ---

@login_required
def add_skill(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            resume, _ = Resume.objects.get_or_create(user=request.user)
            skill.resume = resume
            skill.save()
            return render(request, 'resume/partials/skill_item.html', {'skill': skill})
    else:
        form = SkillForm()
    
    return render(request, 'resume/partials/skill_form.html', {'form': form})

@login_required
@require_http_methods(['DELETE'])
def delete_skill(request, pk):
    skill = get_object_or_404(Skill, pk=pk, resume__user=request.user)
    skill.delete()
    return HttpResponse("")

@login_required
@require_http_methods(['POST'])
def rewrite_description(request):
    try:
        # Rate Limiting
        user_id = request.user.id
        today = date.today().isoformat()
        cache_key = f"ai_limit_{user_id}_{today}"
        
        # Limit: 10 requests per day
        limit = 10
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return HttpResponse(
                f"<textarea class='text-red-400 text-sm mt-1'>Límite diario alcanzado ({limit}/{limit}). Intenta mañana.</textarea>",
                status=429
            )
            
        data = request.POST
        improvement_type = data.get('type', 'experience')  # experience, education, summary, skill
        field_id = data.get('field_id', 'id_description')
        
        # Determine field name and get current text
        if improvement_type == 'summary':
            field_name = 'bio'
            current_text = data.get('bio', '')
        else:
            field_name = 'description'
            current_text = data.get('description', '')
        
        job_title = data.get('job_title', 'Professional')
        
        ai_service = AIService()
        
        if improvement_type == 'experience':
            improved_text = ai_service.improve_description(current_text, job_title)
        elif improvement_type == 'education':
            degree = data.get('degree', 'Carrera')
            institution = data.get('institution', 'Institución')
            improved_text = ai_service.improve_education_description(current_text, degree, institution)
        elif improvement_type == 'summary':
            improved_text = ai_service.improve_summary(current_text, job_title)
        elif improvement_type == 'skill':
            level = data.get('level', 'Intermedio')
            improved_text = ai_service.improve_skill_description(job_title, level)
        else:
            improved_text = ai_service.improve_description(current_text, job_title)
        
        # Increment counter
        cache.set(cache_key, current_count + 1, timeout=86400) # 24 hours timeout
        
        # Return textarea with improved text
        return HttpResponse(
            f'<textarea id="{field_id}" name="{field_name}" class="w-full px-4 py-2 rounded-lg bg-slate-700 border border-slate-600 text-slate-300 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50" rows="4">{improved_text}</textarea>'
        )

    except Exception as e:
        import logging
        logging.error(f"AI Error: {str(e)}")
        return HttpResponse(
            f'<textarea id="id_description" class="w-full px-4 py-2 rounded-lg bg-slate-700 border border-red-600 text-red-400">Error: {str(e)}</textarea>',
            status=500
        )
