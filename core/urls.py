from django.urls import path
from . import views, views_profile, views_connection

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('search/', views.search, name='global_search'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views_profile.profile_view, name='profile'),
    path('profile/edit/', views_profile.profile_edit, name='profile_edit'),
    path('p/<slug:slug>/', views_profile.profile_view, name='public_profile'),
    
    # Profile Posts
    path('profile/post/create/', views_profile.create_profile_post, name='create_profile_post'),
    path('profile/post/<int:post_id>/react/', views_profile.toggle_profile_post_reaction, name='toggle_profile_post_reaction'),
    path('profile/post/<int:post_id>/comment/', views_profile.add_profile_post_comment, name='add_profile_post_comment'),
    path('profile/post/<int:post_id>/comments/', views_profile.load_profile_post_comments, name='load_profile_post_comments'),
    path('profile/post/<int:post_id>/delete/', views_profile.delete_profile_post, name='delete_profile_post'),
    path('profile/comment/<int:comment_id>/delete/', views_profile.delete_profile_post_comment, name='delete_profile_post_comment'),
    
    # Connections
    path('connections/', views_connection.my_connections, name='my_connections'),
    path('connections/send/<int:user_id>/', views_connection.send_request, name='send_connection_request'),
    path('connections/manage/<int:connection_id>/<str:action>/', views_connection.manage_request, name='manage_connection'),
]

