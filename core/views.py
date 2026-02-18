from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm

def index(request):
    """
    Main dashboard view.
    """
    from jobs.services import get_recommended_jobs
    from repository.services import get_recommended_documents
    from resume.services.health_service import calculate_resume_health
    
    recommended_jobs = []
    recommended_docs = []
    resume_health = None
    
    if request.user.is_authenticated:
        recommended_jobs = get_recommended_jobs(request.user, limit=3)
        recommended_docs = get_recommended_documents(request.user, limit=3)
        
        if hasattr(request.user, 'resume'):
            resume_health = calculate_resume_health(request.user.resume)
        
    return render(request, 'core/index.html', {
        'recommended_jobs': recommended_jobs,
        'recommended_docs': recommended_docs,
        'resume_health': resume_health
    })

from .models import UserProfile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile
            UserProfile.objects.create(user=user)
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
        # Add Tailwind classes to standar auth form
        for field in form.fields:
            form.fields[field].widget.attrs.update({
                'class': 'block w-full px-3 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-blue-500 placeholder-slate-500'
            })
            
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('dashboard')

from django.db.models import Q
from jobs.models import JobOffer
from repository.models import Document
from .models import UserProfile

def search(request):
    query = request.GET.get('q', '')
    
    jobs = []
    documents = []
    profiles = []
    
    if query:
        # Search Jobs
        jobs = JobOffer.objects.filter(
            Q(title__icontains=query) | 
            Q(company__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        ).distinct()[:5] # Limit to 5 for now
        
        # Search Documents
        documents = Document.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query),
            is_public=True
        ).distinct()[:5]
        
        # Search Profiles
        profiles = UserProfile.objects.filter(
            Q(title__icontains=query) | 
            Q(bio__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        ).select_related('user').distinct()[:5]
        
    return render(request, 'core/search_results.html', {
        'query': query,
        'jobs': jobs,
        'documents': documents,
        'profiles': profiles,
        'total_results': len(jobs) + len(documents) + len(profiles)
    })

