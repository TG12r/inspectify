from django.urls import path
from . import views, views_profile, views_connection

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('search/', views.search, name='global_search'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views_profile.profile_view, name='profile'),
    path('p/<slug:slug>/', views_profile.profile_view, name='public_profile'),
    # Connections
    path('connections/', views_connection.my_connections, name='my_connections'),
    path('connections/send/<int:user_id>/', views_connection.send_request, name='send_connection_request'),
    path('connections/manage/<int:connection_id>/<str:action>/', views_connection.manage_request, name='manage_connection'),
]
