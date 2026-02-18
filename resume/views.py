from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Resume, Experience, Education, Skill
from .forms import ResumeForm, ExperienceForm, EducationForm, SkillForm

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
        if resume.summary: profile.bio = resume.summary # summary maps to bio (optional, but good for consistency)
        profile.save()
    
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            
            # Sync back: Update Resume model with Profile data to keep Preview working
            resume.title = profile.title
            resume.phone = profile.phone
            resume.address = profile.location
            resume.linkedin_url = profile.linkedin_url
            # We don't sync bio -> summary implies summary is specific to resume, but let's keep them separate for now unless user wants them same.
            # actually, let's sync them for now to avoid confusion
            # resume.summary = profile.bio 
            resume.save()
            
            # Optional: Add a success message
            from django.contrib import messages
            messages.success(request, 'Tu currículum y perfil han sido actualizados exitosamente.')
            return redirect('resume_edit')
    else:
        form = ResumeForm(instance=resume)
        profile_form = UserProfileForm(instance=profile)
    
    
    # Calculate Resume Health
    from .services.health_service import calculate_resume_health
    resume_health = calculate_resume_health(resume)

    context = {
        'form': form,
        'profile_form': profile_form,
        'resume': resume,
        'experiences': resume.experiences.all(),
        'educations': resume.education.all(),
        'skills': resume.skills.all(),
        'resume_health': resume_health,
    }
    return render(request, 'resume/resume_edit.html', context)

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
        from django.core.cache import cache
        from datetime import date
        
        user_id = request.user.id
        today = date.today().isoformat()
        cache_key = f"ai_limit_{user_id}_{today}"
        
        # Limit: 10 requests per day
        limit = 10
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return HttpResponse(
                f"<div class='text-red-400 text-sm mt-1'>Límite diario alcanzado ({limit}/{limit}). Intenta mañana.</div>",
                status=429
            )
            
        data = request.POST
        current_text = data.get('description', '')
        job_title = data.get('job_title', 'Professional')
        
        from .services.ai_service import AIService
        ai_service = AIService()
        
        improved_text = ai_service.improve_description(current_text, job_title)
        
        # Increment counter
        cache.set(cache_key, current_count + 1, timeout=86400) # 24 hours timeout
        
        # Create a form instance with the new data to render the widget correctly
        from .forms import ExperienceForm
        form = ExperienceForm(initial={'description': improved_text})
        
        return HttpResponse(form['description'])

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
