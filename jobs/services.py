from datetime import date
from django.db.models import Q, Count
from .models import JobOffer
from resume.models import Skill, Resume

def get_recommended_jobs(user, limit=5):
    """
    Returns a list of JobOffer objects recommended for the given user
    based on their UserProfile (title, location) and Resume (Skills).
    """
    if not user.is_authenticated:
        return JobOffer.objects.filter(is_active=True).order_by('-posted_at')[:limit]

    # Initialize query
    query = Q(is_active=True)
    
    # 1. Title Match (from UserProfile)
    if hasattr(user, 'profile') and user.profile.title:
        # Simple containment search for now. Could be improved with vector support or similar.
        query |= Q(title__icontains=user.profile.title)

    # 2. Location Match (from UserProfile)
    if hasattr(user, 'profile') and user.profile.location:
        # Match location or Remote
        query |= Q(location__icontains=user.profile.location) | Q(remote=True)

    # 3. Skill Match (from Resume)
    try:
        resume = user.resume
        skills = resume.skills.values_list('name', flat=True)
        
        # Build a query for skills in description
        skill_query = Q()
        for skill in skills:
            skill_query |= Q(description__icontains=skill)
        
        if skills:
            query |= skill_query

    except Resume.DoesNotExist:
        skills = []

    # Execute initial filter
    jobs = JobOffer.objects.filter(query).distinct()
    
    # 4. Scoring / Ordering
    scored_jobs = []
    
    user_title = user.profile.title.lower() if hasattr(user, 'profile') and user.profile.title else ""
    user_location = user.profile.location.lower() if hasattr(user, 'profile') and user.profile.location else ""
    
    for job in jobs[:50]: # limit processing to top 50 candidates from DB
        score = 0
        job_title = job.title.lower()
        job_desc = job.description.lower()
        job_loc = job.location.lower()
        
        # Title match weighting
        if user_title and user_title in job_title:
            score += 10
            
        # Location match weighting
        if user_location and user_location in job_loc:
            score += 5
        if job.remote:
            score += 2
            
        # Skill match weighting
        for skill in skills:
            if skill.lower() in job_desc:
                score += 3
        
        # Recentness weighting
        days_old = 0
        if job.posted_at:
            days_old = (date.today() - job.posted_at).days
            
        if days_old < 7:
            score += 5
        if days_old < 30:
            score += 2

        scored_jobs.append((job, score))
    
    # Sort by score desc, then by date desc
    scored_jobs.sort(key=lambda x: (x[1], x[0].posted_at or x[0].created_at.date()), reverse=True)
    
    # Extract just the job objects
    final_jobs = [job for job, score in scored_jobs]
    
    # Fill with general recent jobs if we don't have enough recommendations
    if len(final_jobs) < limit:
        remaining = limit - len(final_jobs)
        exclude_ids = [j.id for j in final_jobs]
        filler_jobs = JobOffer.objects.filter(is_active=True).exclude(id__in=exclude_ids).order_by('-posted_at')[:remaining]
        final_jobs.extend(filler_jobs)
        
    return final_jobs[:limit]
