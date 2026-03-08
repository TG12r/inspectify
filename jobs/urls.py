from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('create/', views.job_create, name='job_create'),
    path('<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('import/', views.job_import, name='job_import'),
    path('import/format/', views.job_import_format, name='job_import_format'),
    path('trigger-scraping/', views.trigger_scraping, name='trigger_scraping'),
    path('schedule-scraping/', views.schedule_scraping, name='schedule_scraping'),
]
