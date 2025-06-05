
from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('legal-notice/', views.legal_notice, name='legal_notice'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('cookies-policy/', views.cookies_policy, name='cookies_policy'),
    path('cookies-settings/', views.cookies_settings, name='cookies_settings'),
]
