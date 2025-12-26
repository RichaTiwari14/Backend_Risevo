"""
URL configuration for risevo project.

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
from risevoapp.views import *

urlpatterns = [
    # Django Admin - Sirf Superuser
    path('admin/', admin.site.urls),

    # Authentication
    path('api/admin/login/', AdminLoginAPIView.as_view()),
    path('api/admin/logout/', LogoutAPIView.as_view()),
    path('api/admin/profile/', UserProfileAPIView.as_view()),

    # Admin Management - Sirf Superuser create/update/delete kar sakta hai
    path('api/admin/register/', AdminRegisterAPIView.as_view()),
    path('api/admin/register/<int:pk>/', AdminRegisterAPIView.as_view()),

    # Employee Management - Admin aur Superuser dono
    path('api/employee/', EmployeeAPIView.as_view()),
    path('api/employee/<int:pk>/', EmployeeAPIView.as_view()),

    # Enquiry Management
    path('api/enquiry/', EnquiryAPIView.as_view()),
    path('api/enquiry/<int:pk>/', EnquiryAPIView.as_view()),

    # Dashboard
    path('api/dashboard/', DashboardAPIView.as_view()),
]
