from django.shortcuts import render

def landing(request):
    """
    Landing page view for unauthenticated users.
    """
    return render(request, 'core/landing.html')
