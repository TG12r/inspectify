from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_list, name='list'),
    path('publicar/', views.marketplace_create, name='create'),
    path('<int:pk>/', views.marketplace_detail, name='detail'),
    path('<int:pk>/editar/', views.marketplace_edit, name='edit'),
    path('<int:pk>/marcar_vendido/', views.marketplace_mark_sold, name='mark_sold'),
    path('mis-articulos/', views.my_marketplace_items, name='my_items'),
]
