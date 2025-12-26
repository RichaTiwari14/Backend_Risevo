
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, Employee, Enquiry
from .serializers import (
    AdminSerializer, 
    EmployeeSerializer, 
    EnquirySerializer,
    LoginSerializer,
    UserProfileSerializer
)
from risevoapp.permission import IsSuperUser, IsAdminUser, CanCreateAdmin, CanManageEmployee


class AdminLoginAPIView(APIView):
    """
    Login for both Superuser and Admin
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(username=email, password=password)

        if user is None:
            return Response(
                {"error": "Invalid email or password"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is admin or superuser
        if not (user.is_admin or user.is_superuser):
            return Response(
                {"error": "You don't have permission to access dashboard"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:
            return Response(
                {"error": "Account is disabled"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_superuser": user.is_superuser,
                "is_admin": user.is_admin,
                "can_create_admin": user.can_create_admin(),
                "can_create_employee": user.can_create_employee(),
            }
        }, status=status.HTTP_200_OK)


class AdminRegisterAPIView(APIView):
    """
    Admin CRUD - Sirf Superuser create kar sakta hai
    """
    permission_classes = [IsAuthenticated, CanCreateAdmin]

    def post(self, request):
        """Create Admin - Sirf Superuser"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superuser can create admin"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdminSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            admin = serializer.save()
            return Response({
                "message": "Admin registered successfully",
                "admin": AdminSerializer(admin).data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """Get Admins - Admin aur Superuser dono dekh sakte hain"""
        if pk:
            try:
                admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
                serializer = AdminSerializer(admin)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response(
                    {"error": "Admin not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Sirf admins dikhao, superusers nahi
        admins = User.objects.filter(is_admin=True, is_superuser=False)
        serializer = AdminSerializer(admins, many=True)
        return Response({
            "count": admins.count(),
            "admins": serializer.data
        })

    def patch(self, request, pk):
        """Update Admin - Sirf Superuser"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superuser can update admin"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
            serializer = AdminSerializer(admin, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Admin updated successfully",
                    "admin": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response(
                {"error": "Admin not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        """Delete Admin - Sirf Superuser"""
        if not request.user.is_superuser:
            return Response(
                {"error": "Only superuser can delete admin"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
            admin_email = admin.email
            admin.delete()
            return Response({
                "message": f"Admin '{admin_email}' deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "Admin not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class EmployeeAPIView(APIView):
    """
    Employee CRUD - Admin aur Superuser dono manage kar sakte hain
    """
    permission_classes = [IsAuthenticated, CanManageEmployee]

    def post(self, request):
        """Create Employee"""
        serializer = EmployeeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            employee = serializer.save()
            return Response({
                "message": "Employee created successfully",
                "employee": EmployeeSerializer(employee).data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """Get Employees"""
        if pk:
            try:
                employee = Employee.objects.get(pk=pk)
                serializer = EmployeeSerializer(employee)
                return Response(serializer.data)
            except Employee.DoesNotExist:
                return Response(
                    {"error": "Employee not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

        employees = Employee.objects.all().order_by('-created_at')
        serializer = EmployeeSerializer(employees, many=True)
        return Response({
            "count": employees.count(),
            "employees": serializer.data
        })

    def patch(self, request, pk):
        """Update Employee"""
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = EmployeeSerializer(employee, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Employee updated successfully",
                    "employee": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        """Delete Employee"""
        try:
            employee = Employee.objects.get(pk=pk)
            employee_name = employee.name
            employee.delete()
            return Response({
                "message": f"Employee '{employee_name}' deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )



class UserProfileAPIView(APIView):
    """
    Current User Profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "user": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    Logout - Blacklist refresh token
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                "message": "Logout successful"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "message": "Logout successful"
            }, status=status.HTTP_200_OK)

class EnquiryAPIView(APIView):
    def post(self, request):
        serializer = EnquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        enquiries = Enquiry.objects.all()
        serializer = EnquirySerializer(enquiries, many=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            enquiry = Enquiry.objects.get(pk=pk)
            enquiry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Enquiry.DoesNotExist:
            return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)     



class DashboardAPIView(APIView):
    def get(self, request):
        return Response({
            "total_admin": User.objects.filter(is_admin=True).count(),
            "total_employee": Employee.objects.count(),
            "today_enquiry": Enquiry.objects.filter(created_at__date=now().date()).count(),
            "total_enquiry": Enquiry.objects.count()
        })               
