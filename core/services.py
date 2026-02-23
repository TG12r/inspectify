from django.db.models import Q, Count


def get_recommended_people(user, limit=4):
    """
    Recommend users to connect with, based on shared skills and similar titles.
    Excludes already connected users or those with pending requests.
    """
    from .models import Connection, UserProfile

    # Get IDs of users already connected or with pending request
    excluded_ids = set()
    excluded_ids.add(user.id)

    existing_connections = Connection.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).exclude(status='REJECTED')

    for conn in existing_connections:
        excluded_ids.add(conn.sender_id)
        excluded_ids.add(conn.receiver_id)

    # Base queryset: all other profiles
    candidates = UserProfile.objects.exclude(
        user_id__in=excluded_ids
    ).select_related('user').prefetch_related('user__resume__skills')

    # Score and collect
    scored = []
    try:
        my_skills = set(
            user.resume.skills.values_list('name', flat=True)
        )
        my_title = getattr(user.profile, 'title', '') or ''
    except Exception:
        my_skills = set()
        my_title = ''

    for profile in candidates:
        score = 0

        # +2 per shared skill
        try:
            their_skills = set(
                profile.user.resume.skills.values_list('name', flat=True)
            )
            shared = my_skills & their_skills
            score += len(shared) * 2
        except Exception:
            pass

        # +3 for similar title keyword match
        their_title = profile.title or ''
        if my_title and their_title:
            my_words = set(my_title.lower().split())
            their_words = set(their_title.lower().split())
            if my_words & their_words:
                score += 3

        # +1 for same location
        try:
            if profile.location and user.profile.location:
                if profile.location.lower() == user.profile.location.lower():
                    score += 1
        except Exception:
            pass

        scored.append((score, profile))

    # Sort descending, return top N
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]


def get_recommended_posts(user, limit=5):
    """
    Recommend profile posts to user.
    Returns: {'friends': [...], 'all': [...]}
    
    Algorithm:
    - Friends posts: Posts from connected users, sorted by reactions + comments
    - All posts: Top posts by engagement, excluding self posts
    """
    from .models import Connection, ProfilePost
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get user's connections
    connections = Connection.objects.filter(
        Q(sender=user, status='ACCEPTED') | Q(receiver=user, status='ACCEPTED')
    )
    
    connected_user_ids = set()
    for conn in connections:
        if conn.sender_id == user.id:
            connected_user_ids.add(conn.receiver_id)
        else:
            connected_user_ids.add(conn.sender_id)
    
    # Posts from friends (last 30 days, sorted by engagement)
    friends_posts = (
        ProfilePost.objects
        .filter(author_id__in=connected_user_ids)
        .annotate(engagement=Count('reactions') + Count('comments'))
        .order_by('-engagement', '-created_at')
        .select_related('author__profile')
        .prefetch_related('reactions', 'comments')
        [:limit]
    )
    
    # All posts (excluding user's own posts, last 30 days)
    recent_threshold = timezone.now() - timedelta(days=30)
    all_posts = (
        ProfilePost.objects
        .exclude(author=user)
        .filter(created_at__gte=recent_threshold)
        .annotate(engagement=Count('reactions') + Count('comments'))
        .order_by('-engagement', '-created_at')
        .select_related('author__profile')
        .prefetch_related('reactions', 'comments')
        [:limit]
    )
    
    # Add reaction type for each post
    for post in friends_posts:
        post.user_reaction_type = post.get_user_reaction(user)
        
    for post in all_posts:
        post.user_reaction_type = post.get_user_reaction(user)
    
    return {
        'friends': friends_posts,
        'all': all_posts,
    }

