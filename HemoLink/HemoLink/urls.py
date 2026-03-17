"""
URL configuration for HemoLink project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_register, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.donor_dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('requests/', views.active_requests, name='requests'),
    path('requests/<int:request_id>/pledge/', views.pledge_request, name='pledge_request'),
    path('requests/<int:request_id>/fulfill/', views.fulfill_request, name='fulfill_request'),
    path('status/', views.notifications_status, name='status'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('blood-banks/', views.blood_banks, name='blood_banks'),
]
