from rest_framework.permissions import BasePermission


class IsAdminOrSuperUser(BasePermission):
    """
    Admin ya Superuser - Sab kuch access (except Django Admin)
    """
    message = "Sirf admin ya superuser ye action kar sakta hai."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_superuser)
        )


class CanManageAdmin(BasePermission):
    """
    Admin CRUD - Admin aur Superuser dono kar sakte hain
    """
    message = "Admin management ke liye permission chahiye."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_admin()
        )


class CanManageEmployee(BasePermission):
    """
    Employee CRUD - Admin aur Superuser dono
    """
    message = "Employee management ke liye permission chahiye."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_employee()
        )


class CanManageEnquiry(BasePermission):
    """
    Enquiry CRUD - Admin aur Superuser dono
    """
    message = "Enquiry management ke liye permission chahiye."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_enquiry()
        )