from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.resume_edit, name='resume_edit'),
    path('preview/', views.resume_preview, name='resume_preview'),
    path('experience/add/', views.add_experience, name='add_experience'),
    path('experience/<int:pk>/edit/', views.edit_experience, name='edit_experience'),
    path('experience/<int:pk>/delete/', views.delete_experience, name='delete_experience'),
    
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:pk>/edit/', views.edit_education, name='edit_education'),
    path('education/<int:pk>/delete/', views.delete_education, name='delete_education'),

    path('skill/add/', views.add_skill, name='add_skill'),
    path('skill/<int:pk>/delete/', views.delete_skill, name='delete_skill'),
    path('rewrite-description/', views.rewrite_description, name='rewrite_description'),
]
