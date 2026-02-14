from django.shortcuts import render, get_object_or_404
from .models import JobOffer
from django.core.paginator import Paginator

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
