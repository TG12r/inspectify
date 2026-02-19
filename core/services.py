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
