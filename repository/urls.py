from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='repository_index'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('doc/<slug:slug>/', views.document_detail, name='document_detail'),
]
