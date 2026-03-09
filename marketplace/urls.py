from django.urls import path
from . import views, views_servicios

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_list, name='list'),
    path('publicar/', views.marketplace_create, name='create'),
    path('<int:pk>/', views.marketplace_detail, name='detail'),
    path('<int:pk>/editar/', views.marketplace_edit, name='edit'),
    path('<int:pk>/marcar_vendido/', views.marketplace_mark_sold, name='mark_sold'),
    path('mis-articulos/', views.my_marketplace_items, name='my_items'),

    # Freelance services
    path('servicios/', views_servicios.servicios_list, name='servicios_list'),
    path('servicios/publicar/', views_servicios.servicios_create, name='servicios_create'),
    path('servicios/<int:pk>/', views_servicios.servicios_detail, name='servicios_detail'),
    path('servicios/<int:pk>/editar/', views_servicios.servicios_edit, name='servicios_edit'),
    path('mis-servicios/', views_servicios.mis_servicios, name='mis_servicios'),
]
