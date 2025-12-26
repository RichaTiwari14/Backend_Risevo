from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Sirf Superuser access - Django Admin + Dashboard dono
    """
    message = "Only superuser can access this resource."

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_superuser
        )


class IsAdminUser(BasePermission):
    """
    Admin ya Superuser access - Dashboard
    """
    message = "Only admin users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_superuser)
        )


class CanCreateAdmin(BasePermission):
    """
    Sirf Superuser admin create kar sakta hai
    """
    message = "Only superuser can create admin users."

    def has_permission(self, request, view):
        if request.method in ['POST']:
            return (
                request.user and 
                request.user.is_authenticated and 
                request.user.is_superuser
            )
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_superuser)
        )


class CanManageEmployee(BasePermission):
    """
    Admin aur Superuser dono employee manage kar sakte hain
    """
    message = "Only admin users can manage employees."

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_superuser)
        )