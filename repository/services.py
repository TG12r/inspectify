from django.db.models import Q
from .models import Document

def get_recommended_documents(user, limit=5):
    """
    Returns a list of recommended documents for the given user.
    Strategy:
    1. Filter by keywords from user.profile.title (if available).
    2. Fallback/Fill with most viewed documents.
    """
    recommended = []
    
    # 1. Profile-based recommendations
    if user.is_authenticated and hasattr(user, 'profile') and user.profile.title:
        # Extract keywords (simple split by space, ignoring small words could be added)
        keywords = [w for w in user.profile.title.split() if len(w) > 2]
        
        if keywords:
            query = Q()
            for word in keywords:
                query |= Q(title__icontains=word) | Q(description__icontains=word) | Q(category__name__icontains=word)
            
            # Get matches, excluding already seen (though list is empty now)
            matches = Document.objects.filter(query, is_public=True).order_by('-views', '-uploaded_at')[:limit]
            recommended.extend(matches)
            
    # 2. Fill with popular documents if we haven't reached the limit
    if len(recommended) < limit:
        needed = limit - len(recommended)
        existing_ids = [d.id for d in recommended]
        
        popular = Document.objects.filter(is_public=True).exclude(id__in=existing_ids).order_by('-views', '-uploaded_at')[:needed]
        recommended.extend(popular)
        
    return recommended[:limit]
