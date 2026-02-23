from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_list, name='community_list'),
    path('create/', views.community_create, name='community_create'),
    path('<slug:slug>/', views.community_detail, name='community_detail'),
    path('<slug:slug>/join/', views.toggle_membership, name='toggle_membership'),
    path('<slug:slug>/post/', views.create_post, name='create_post'),
    path('share-job/<int:job_id>/', views.share_job_to_communities, name='share_job_to_communities'),
    
    # Reacciones y comentarios
    path('post/<int:post_id>/react/', views.toggle_reaction, name='toggle_reaction'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comments/', views.load_comments, name='load_comments'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
