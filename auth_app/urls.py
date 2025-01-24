from django.urls import path
from . import views
from .views import TestDataAPIView, DynamicDataAPIView, CreateDynamicDataAPIView


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify/', views.verify_view, name='verify'),
    path('test/', TestDataAPIView.as_view(), name='test-data'),
    path('dynamic-data/', DynamicDataAPIView.as_view(), name='dynamic-data'),
    path('create/', CreateDynamicDataAPIView.as_view(), name='create-dynamic-data'),

    path('', views.home_view, name='home'),
]