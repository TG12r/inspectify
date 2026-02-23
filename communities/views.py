from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count

from .models import Community, CommunityMember, Post, PostReaction, PostComment
from jobs.models import JobOffer


def community_list(request):
    communities = Community.objects.annotate(
        total_members=Count('memberships')
    ).order_by('-total_members')

    user_memberships = set()
    if request.user.is_authenticated:
        user_memberships = set(
            CommunityMember.objects.filter(user=request.user).values_list('community_id', flat=True)
        )

    return render(request, 'communities/list.html', {
        'communities': communities,
        'user_memberships': user_memberships,
    })


def community_detail(request, slug):
    community = get_object_or_404(Community, slug=slug)
    posts = community.posts.select_related('author__profile', 'job_offer').all()
    members = community.memberships.select_related('user__profile').order_by('-role', 'joined_at')[:10]
    is_member = community.is_member(request.user)
    
    # Agregar la reacción del usuario a cada post como atributo temporal
    if request.user.is_authenticated:
        for post in posts:
            post.user_reaction_type = post.get_user_reaction(request.user)
    
    # Contar posts por tipo
    from django.db.models import Count, Q
    post_stats = {
        'total': posts.count(),
        'offers': posts.filter(post_type='OFFER').count(),
        'questions': posts.filter(post_type='QUESTION').count(),
        'news': posts.filter(post_type='NEWS').count(),
        'general': posts.filter(post_type='GENERAL').count(),
    }

    return render(request, 'communities/detail.html', {
        'community': community,
        'posts': posts,
        'members': members,
        'is_member': is_member,
        'post_stats': post_stats,
    })


@login_required
def community_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'GENERAL')
        privacy = request.POST.get('privacy', 'OPEN')

        if not name:
            return render(request, 'communities/create.html', {
                'error': 'El nombre es obligatorio.',
                'categories': Community.CATEGORY_CHOICES,
            })

        community = Community.objects.create(
            name=name,
            description=description,
            category=category,
            privacy=privacy,
            created_by=request.user,
        )
        # Creator becomes admin member
        CommunityMember.objects.create(community=community, user=request.user, role='ADMIN')
        return redirect('community_detail', slug=community.slug)

    return render(request, 'communities/create.html', {
        'categories': Community.CATEGORY_CHOICES,
    })


@login_required
def toggle_membership(request, slug):
    community = get_object_or_404(Community, slug=slug)
    membership = CommunityMember.objects.filter(community=community, user=request.user).first()

    if membership:
        # Don't let the only admin leave
        if membership.role == 'ADMIN' and community.memberships.filter(role='ADMIN').count() == 1:
            return HttpResponse("""
                <button class="px-4 py-2 rounded-lg text-sm font-medium bg-red-900/20 text-red-400 border border-red-800 cursor-not-allowed" disabled>
                    Eres el único admin
                </button>
            """)
        membership.delete()
        joined = False
    else:
        CommunityMember.objects.create(community=community, user=request.user, role='MEMBER')
        joined = True

    member_count = community.memberships.count()

    if joined:
        html = f"""
            <div id="join-section">
                <button hx-post="/communities/{community.slug}/join/" hx-target="#join-section" hx-swap="outerHTML"
                    class="px-4 py-2 rounded-lg text-sm font-medium bg-slate-700 hover:bg-slate-600 text-white transition-colors">
                    Abandonar
                </button>
                <span class="text-slate-400 text-sm">{member_count} miembro{'s' if member_count != 1 else ''}</span>
            </div>
        """
    else:
        html = f"""
            <div id="join-section">
                <button hx-post="/communities/{community.slug}/join/" hx-target="#join-section" hx-swap="outerHTML"
                    class="px-4 py-2 rounded-lg text-sm font-medium bg-purple-600 hover:bg-purple-700 text-white transition-colors">
                    Unirse
                </button>
                <span class="text-slate-400 text-sm">{member_count} miembro{'s' if member_count != 1 else ''}</span>
            </div>
        """
    return HttpResponse(html)


@login_required
def create_post(request, slug):
    community = get_object_or_404(Community, slug=slug)

    if not community.is_member(request.user):
        return HttpResponse("Debes ser miembro para publicar.", status=403)

    content = request.POST.get('content', '').strip()
    post_type = request.POST.get('post_type', 'GENERAL')

    if not content:
        return HttpResponse("", status=204)

    post = Post.objects.create(
        community=community,
        author=request.user,
        content=content,
        post_type=post_type,
    )
    
    # Agregar la reacción del usuario al post (ninguna en este caso)
    post.user_reaction_type = None

    return render(request, 'communities/_post_card.html', {'post': post})


@login_required
def share_job_to_communities(request, job_id):
    """Vista para compartir una oferta de trabajo en comunidades"""
    job = get_object_or_404(JobOffer, id=job_id)
    
    # Obtener comunidades donde el usuario es miembro
    user_communities = Community.objects.filter(memberships__user=request.user)
    
    if request.method == 'POST':
        selected_communities = request.POST.getlist('communities')
        comment = request.POST.get('comment', '').strip()
        
        if not selected_communities:
            return JsonResponse({'error': 'Debes seleccionar al menos una comunidad'}, status=400)
        
        # Crear post en cada comunidad seleccionada
        posts_created = 0
        for community_id in selected_communities:
            community = get_object_or_404(Community, id=community_id, memberships__user=request.user)
            
            # Contenido del post
            content = f"{comment}\n\n" if comment else ""
            content += f"🔗 {job.title} en {job.company}"
            if job.location:
                content += f"\n📍 {job.location}"
            if job.salary_range:
                content += f"\n💰 {job.salary_range}"
            
            Post.objects.create(
                community=community,
                author=request.user,
                content=content,
                post_type='OFFER',
                job_offer=job,
            )
            posts_created += 1
        
        return JsonResponse({
            'success': True, 
            'message': f'Oferta compartida en {posts_created} comunidad{"es" if posts_created != 1 else ""}'
        })
    
    # GET request - mostrar modal con comunidades
    return render(request, 'jobs/_share_job_modal.html', {
        'job': job,
        'communities': user_communities,
    })


@login_required
def toggle_reaction(request, post_id):
    """Toggle o cambiar reacción en un post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar que el usuario sea miembro de la comunidad
    if not post.community.is_member(request.user):
        return HttpResponse("Debes ser miembro para reaccionar.", status=403)
    
    reaction_type = request.POST.get('reaction_type', 'LIKE')
    
    # Buscar si ya tiene una reacción
    existing_reaction = PostReaction.objects.filter(post=post, user=request.user).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Si es la misma reacción, la eliminamos (toggle)
            existing_reaction.delete()
        else:
            # Si es diferente, la actualizamos
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
    else:
        # Crear nueva reacción
        PostReaction.objects.create(
            post=post,
            user=request.user,
            reaction_type=reaction_type
        )
    
    # Refrescar el post desde la DB para obtener los datos actualizados
    post.refresh_from_db()
    
    # Agregar la reacción del usuario como atributo temporal
    post.user_reaction_type = post.get_user_reaction(request.user)
    
    # Retornar la sección de reacciones actualizada
    context = {
        'post': post,
        'user': request.user,
    }
    
    return render(request, 'communities/_post_reactions.html', context)


@login_required
def add_comment(request, post_id):
    """Agregar un comentario a un post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar que el usuario sea miembro de la comunidad
    if not post.community.is_member(request.user):
        return HttpResponse("Debes ser miembro para comentar.", status=403)
    
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return HttpResponse("", status=204)
    
    parent = None
    if parent_id:
        parent = get_object_or_404(PostComment, id=parent_id)
    
    comment = PostComment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent
    )
    
    # Retornar el comentario individual
    return render(request, 'communities/_comment_item.html', {'comment': comment, 'user': request.user})


@login_required
def load_comments(request, post_id):
    """Cargar todos los comentarios de un post"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent=None).select_related('author__profile').prefetch_related('replies__author__profile')
    
    return render(request, 'communities/_comments_section.html', {
        'post': post,
        'comments': comments,
        'user': request.user
    })


@login_required
def delete_comment(request, comment_id):
    """Eliminar un comentario (solo el autor o admin)"""
    comment = get_object_or_404(PostComment, id=comment_id)
    
    # Verificar permisos
    is_admin = CommunityMember.objects.filter(
        community=comment.post.community,
        user=request.user,
        role='ADMIN'
    ).exists()
    
    if comment.author != request.user and not is_admin:
        return HttpResponse("No tienes permiso para eliminar este comentario.", status=403)
    
    comment.delete()
    return HttpResponse("", status=204)

