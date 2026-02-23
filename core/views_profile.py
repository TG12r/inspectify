from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Connection, ProfilePost, ProfilePostReaction, ProfilePostComment
from django.contrib import messages
from django import forms
from django.db.models import Q
from django.http import HttpResponse

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'title', 'bio', 'location', 'phone', 'years_of_experience', 
                  'willing_to_travel', 'offshore_experience', 'has_driving_license', 'linkedin_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

from django.contrib.auth import get_user_model

# Removed @login_required to allow public access, handled inside
def profile_view(request, slug=None):
    User = get_user_model()
    
    if slug:
        # Public view: anyone can see if slug exists
        profile = get_object_or_404(UserProfile, slug=slug)
        user_obj = profile.user
        is_owner = request.user == user_obj
    else:
        # Private view: must be logged in to see own profile
        if not request.user.is_authenticated:
            return redirect('login')
        user_obj = request.user
        profile, created = UserProfile.objects.get_or_create(user=user_obj)
        is_owner = True
    
    # Get resume related data
    try:
        resume = user_obj.resume
        experiences = resume.experiences.all().order_by('-start_date')
        education = resume.education.all().order_by('-start_date')
        skills = resume.skills.all().order_by('-level')
    except:
        resume = None
        experiences = []
        education = []
        skills = []
    
    # Connection status for the Connect button
    connection_status = None
    connection = None
    if request.user.is_authenticated and not is_owner:
        conn = Connection.objects.filter(
            Q(sender=request.user, receiver=user_obj) |
            Q(sender=user_obj, receiver=request.user)
        ).first()
        if conn:
            connection = conn
            if conn.status == 'ACCEPTED':
                connection_status = 'ACCEPTED'
            elif conn.status == 'PENDING' and conn.sender == request.user:
                connection_status = 'PENDING_SENT'
            elif conn.status == 'PENDING' and conn.receiver == request.user:
                connection_status = 'PENDING_RECEIVED'

    # Get user's posts
    posts = user_obj.profile_posts.select_related('author__profile').prefetch_related('reactions', 'comments').order_by('-created_at')
    
    # Add user reaction to each post
    if request.user.is_authenticated:
        for post in posts:
            post.user_reaction_type = post.get_user_reaction(request.user)

    return render(request, 'core/profile_detail.html', {
        'profile': profile,
        'user': user_obj,
        'is_owner': is_owner,
        'resume': resume,
        'experiences': experiences,
        'education': education,
        'skills': skills,
        'connection_status': connection_status,
        'connection': connection,
        'posts': posts,
    })

@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'core/profile_edit.html', {'form': form, 'profile': profile})


@login_required
def create_profile_post(request):
    """Crear un post en el perfil del usuario"""
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        post_type = request.POST.get('post_type', 'GENERAL')
        title = request.POST.get('title', '').strip()
        link = request.POST.get('link', '').strip()
        image = request.FILES.get('image')
        
        if not content:
            return HttpResponse("", status=204)
        
        post = ProfilePost.objects.create(
            author=request.user,
            content=content,
            post_type=post_type,
            title=title if title else None,
            link=link if link else None,
            image=image
        )
        
        # Agregar la reacción del usuario al post (ninguna en este caso)
        post.user_reaction_type = None
        
        return render(request, 'core/_profile_post_card.html', {'post': post, 'user': request.user})
    
    return HttpResponse("Método no permitido", status=405)


@login_required
def toggle_profile_post_reaction(request, post_id):
    """Toggle o cambiar reacción en un post de perfil"""
    post = get_object_or_404(ProfilePost, id=post_id)
    
    reaction_type = request.POST.get('reaction_type', 'LIKE')
    
    # Buscar si ya tiene una reacción
    existing_reaction = ProfilePostReaction.objects.filter(post=post, user=request.user).first()
    
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
        ProfilePostReaction.objects.create(
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
    
    return render(request, 'core/_profile_post_reactions.html', context)


@login_required
def add_profile_post_comment(request, post_id):
    """Agregar un comentario a un post de perfil"""
    post = get_object_or_404(ProfilePost, id=post_id)
    
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return HttpResponse("", status=204)
    
    parent = None
    if parent_id:
        parent = get_object_or_404(ProfilePostComment, id=parent_id)
    
    comment = ProfilePostComment.objects.create(
        post=post,
        author=request.user,
        content=content,
        parent=parent
    )
    
    # Retornar el comentario individual
    return render(request, 'core/_profile_comment_item.html', {'comment': comment, 'user': request.user})


@login_required
def load_profile_post_comments(request, post_id):
    """Cargar todos los comentarios de un post de perfil"""
    post = get_object_or_404(ProfilePost, id=post_id)
    comments = post.comments.filter(parent=None).select_related('author__profile').prefetch_related('replies__author__profile')
    
    return render(request, 'core/_profile_comments_section.html', {
        'post': post,
        'comments': comments,
        'user': request.user
    })


@login_required
def delete_profile_post_comment(request, comment_id):
    """Eliminar un comentario de post de perfil (solo el autor)"""
    comment = get_object_or_404(ProfilePostComment, id=comment_id)
    
    # Verificar que sea el autor
    if comment.author != request.user:
        return HttpResponse("No tienes permiso para eliminar este comentario.", status=403)
    
    comment.delete()
    return HttpResponse("", status=200)


@login_required
def delete_profile_post(request, post_id):
    """Eliminar un post de perfil (solo el autor)"""
    post = get_object_or_404(ProfilePost, id=post_id)
    
    # Verificar que sea el autor
    if post.author != request.user:
        return HttpResponse("No tienes permiso para eliminar este post.", status=403)
    
    post.delete()
    return HttpResponse("", status=200)

