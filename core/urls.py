from django.urls import path
from . import views, views_profile

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views_profile.profile_view, name='profile'),
    path('p/<slug:slug>/', views_profile.profile_view, name='public_profile'),
]
