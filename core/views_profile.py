from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib import messages
from django import forms

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'title', 'bio', 'location', 'phone', 'years_of_experience', 
                  'willing_to_travel', 'offshore_experience', 'has_driving_license', 'linkedin_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

from django.contrib.auth import get_user_model

# Removed @login_required to allow public access, handled inside
def profile_view(request, slug=None):
    User = get_user_model()
    
    if slug:
        # Public view: anyone can see if slug exists
        profile = get_object_or_404(UserProfile, slug=slug)
        user_obj = profile.user
        is_owner = request.user == user_obj
    else:
        # Private view: must be logged in to see own profile
        if not request.user.is_authenticated:
            return redirect('login')
        user_obj = request.user
        profile, created = UserProfile.objects.get_or_create(user=user_obj)
        is_owner = True
    
    # Get resume related data
    try:
        resume = user_obj.resume
        experiences = resume.experiences.all().order_by('-start_date')
        education = resume.education.all().order_by('-start_date')
        skills = resume.skills.all().order_by('-level')
    except:
        resume = None
        experiences = []
        education = []
        skills = []
    
    return render(request, 'core/profile_detail.html', {
        'profile': profile,
        'user_obj': user_obj, # Pass specific user object
        'is_owner': is_owner,
        'resume': resume,
        'experiences': experiences,
        'education': education,
        'skills': skills
    })

@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'core/profile_edit.html', {'form': form, 'profile': profile})
