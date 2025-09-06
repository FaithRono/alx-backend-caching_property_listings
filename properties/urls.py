from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # API endpoints
    path('', views.property_list, name='property_list'),
    path('html/', views.property_list_html, name='property_list_html'),
    path('<int:property_id>/', views.property_detail, name='property_detail'),
    
    # Cache management endpoints
    path('cache/metrics/', views.cache_metrics, name='cache_metrics'),
    path('cache/clear/', views.clear_cache, name='clear_cache'),
]
