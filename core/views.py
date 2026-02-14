from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm

def index(request):
    """
    Main dashboard view.
    """
    from jobs.services import get_recommended_jobs
    from repository.services import get_recommended_documents
    
    recommended_jobs = []
    recommended_docs = []
    
    if request.user.is_authenticated:
        recommended_jobs = get_recommended_jobs(request.user, limit=3)
        recommended_docs = get_recommended_documents(request.user, limit=3)
        
    return render(request, 'core/index.html', {
        'recommended_jobs': recommended_jobs,
        'recommended_docs': recommended_docs
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
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

def logout_view(request):
    logout(request)
    return redirect('dashboard')
