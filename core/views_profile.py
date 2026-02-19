from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Connection
from django.contrib import messages
from django import forms
from django.db.models import Q

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
    
    # Connection status for the Connect button
    connection_status = None
    connection = None
    if request.user.is_authenticated and not is_owner:
        conn = Connection.objects.filter(
            Q(sender=request.user, receiver=user_obj) |
            Q(sender=user_obj, receiver=request.user)
        ).first()
        if conn:
            connection = conn
            if conn.status == 'ACCEPTED':
                connection_status = 'ACCEPTED'
            elif conn.status == 'PENDING' and conn.sender == request.user:
                connection_status = 'PENDING_SENT'
            elif conn.status == 'PENDING' and conn.receiver == request.user:
                connection_status = 'PENDING_RECEIVED'

    return render(request, 'core/profile_detail.html', {
        'profile': profile,
        'user': user_obj,
        'is_owner': is_owner,
        'resume': resume,
        'experiences': experiences,
        'education': education,
        'skills': skills,
        'connection_status': connection_status,
        'connection': connection,
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
