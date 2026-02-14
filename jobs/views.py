from django.shortcuts import render, get_object_or_404, redirect
from .models import JobOffer
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.management import call_command

@staff_member_required
def trigger_scraping(request):
    if request.method == 'POST':
        try:
            # Get params from modal form
            keywords = request.POST.get('keywords', 'API 510')
            source = request.POST.get('source', 'all')
            location = request.POST.get('location', '')
            limit = int(request.POST.get('limit', 10))
            
            # Handle 'TODAS' keyword logic (same as in tasks.py)
            if keywords.upper() in ['TODAS', 'ALL']:
                default_keywords = ['API 510', 'API 570', 'API 653', 'CWI', 'NDT', 'Welding Inspector', 'QA/QC Inspector']
                for kw in default_keywords:
                    call_command('scrape_jobs', source=source, keywords=kw, location=location, limit=limit)
            else:
                call_command('scrape_jobs', source=source, keywords=keywords, location=location, limit=limit)
                
            messages.success(request, f'Scraping manual ejecutado: {keywords} en {source}')
        except Exception as e:
            messages.error(request, f'Error al ejecutar scraping: {str(e)}')
            
        return redirect('admin:index')
    
    return redirect('admin:index')

@staff_member_required
def schedule_scraping(request):
    if request.method == 'POST':
        try:
            # Get params from modal form
            keywords = request.POST.get('keywords', 'API 510')
            source = request.POST.get('source', 'all')
            location = request.POST.get('location', '')
            limit = int(request.POST.get('limit', 10))
            frequency = request.POST.get('frequency', 'daily')
            
            # Calculate repeat interval
            repeat = None
            if frequency == 'daily':
                repeat = 24 * 60 * 60
            elif frequency == 'weekly':
                repeat = 7 * 24 * 60 * 60
            elif frequency == 'monthly':
                repeat = 30 * 24 * 60 * 60
            # 'once' implies repeat=None (default)

            # Schedule daily task
            from jobs.tasks import scrape_all_jobs_task
            
            # We allow multiple schedules with different params. 
            # To prevent exact duplicates, we could check args, but for now let's just schedule it.
            # The verbose_name or checking specific args in Task model is complex with hashing.
            # We will just schedule it. User can manage duplicates in Django Admin > Background Tasks if needed.
            
            scrape_all_jobs_task(
                keywords=keywords, 
                source=source, 
                location=location, 
                limit=limit, 
                repeat=repeat
            )
            
            freq_label = {
                'daily': 'Diariamente',
                'weekly': 'Semanalmente',
                'monthly': 'Mensualmente',
                'once': 'Una vez'
            }.get(frequency, 'Diariamente')
            
            messages.success(request, f'Scraping programado: {keywords} en {source} ({freq_label})')
            
        except Exception as e:
            messages.error(request, f'Error al programar scraping: {str(e)}')
            
        return redirect('admin:index')
    
    return redirect('admin:index')

def job_list(request):
    jobs = JobOffer.objects.filter(is_active=True)
    
    # Filter by search query
    query = request.GET.get('q')
    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(company__icontains=query) | jobs.filter(description__icontains=query)
    
    # Filter by location
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)

    # Filter by source
    source = request.GET.get('source')
    if source:
        jobs = jobs.filter(source__iexact=source)

    # Filter by remote
    is_remote = request.GET.get('remote')
    if is_remote == 'on':
        jobs = jobs.filter(remote=True)
    
    # Filter by salary (basic implementation, assumes salary_min is populated or we filter by text range if needed)
    # For now, let's just filter if we had the field populated. 
    # Since we are scraping text, precise numeric filtering is hard without parsing.
    # We will skip numeric filtering for now unless we parsed it.

    # Ordering
    sort_by = request.GET.get('sort', '-posted_at')
    if sort_by in ['posted_at', '-posted_at', 'salary', '-salary']:
        jobs = jobs.order_by(sort_by)

    # Pagination
    paginator = Paginator(jobs, 10) # 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'jobs': page_obj, # Pass page_obj instead of jobs
        'query': query,
        'location': location,
        'selected_source': source,
        'is_remote': is_remote,
        'sort_by': sort_by,
        'sources': JobOffer.objects.values_list('source', flat=True).distinct().order_by('source')
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, pk):
    job = get_object_or_404(JobOffer, pk=pk)
    return render(request, 'jobs/job_detail.html', {'job': job})
