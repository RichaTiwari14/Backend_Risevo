from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from risevoapp.views import (
    AdminLoginAPIView,
    LogoutAPIView,
    UserProfileAPIView,
    AdminRegisterAPIView,
    EmployeeAPIView,
    EnquiryAPIView,
    DashboardAPIView,
    CareerAPIView,
    JobApplicationAPIView,
)

urlpatterns = [
    # =========================
    # DJANGO ADMIN
    # =========================
    path("admin/", admin.site.urls),

    # =========================
    # AUTHENTICATION
    # =========================
    path("api/admin/login/", AdminLoginAPIView.as_view()),
    path("api/admin/logout/", LogoutAPIView.as_view()),
    path("api/admin/profile/", UserProfileAPIView.as_view()),

    # =========================
    # ADMIN MANAGEMENT (SUPERUSER)
    # =========================
    path("api/admin/register/", AdminRegisterAPIView.as_view()),
    path("api/admin/register/<int:pk>/", AdminRegisterAPIView.as_view()),

    # =========================
    # EMPLOYEE MANAGEMENT
    # =========================
    path("api/employee/", EmployeeAPIView.as_view()),
    path("api/employee/<int:pk>/", EmployeeAPIView.as_view()),

    # =========================
    # ENQUIRY
    # =========================
    path("api/enquiry/", EnquiryAPIView.as_view()),
    path("api/enquiry/<int:pk>/", EnquiryAPIView.as_view()),

    # =========================
    # DASHBOARD
    # =========================
    path("api/dashboard/", DashboardAPIView.as_view()),

    # Career
    path("api/career/", CareerAPIView.as_view()),
    path("api/career/<int:pk>/", CareerAPIView.as_view()),

# Job Apply
    path("api/job-apply/", JobApplicationAPIView.as_view()),
    path("api/job-apply/<int:pk>/", JobApplicationAPIView.as_view()),
]

# =========================
# MEDIA FILES (SAFE)
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

