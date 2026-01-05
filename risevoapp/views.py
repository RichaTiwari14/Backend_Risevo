from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.timezone import now

from .models import Career, User, Employee, Enquiry , JobApplication
from .serializers import (
    AdminSerializer, 
    EmployeeSerializer, 
    EnquirySerializer,
    LoginSerializer,
    UserProfileSerializer,
   CareerSerializer,
   JobApplicationSerializer  ,   
)
from .permission import (
    IsAdminOrSuperUser,
    CanManageAdmin,
    CanManageEmployee,
    CanManageEnquiry,
)

from django.db.models.functions import TruncMonth
from django.db.models import Count
from calendar import month_abbr

# ==================== AUTH APIs ====================

class AdminLoginAPIView(APIView):
    """
    Login API for Admin and Superuser
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

        if not user.can_access_dashboard():
            return Response(
                {"error": "Dashboard access permission nahi hai"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:
            return Response(
                {"error": "Account disabled hai"}, 
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
                "permissions": {
                    "can_manage_admin": user.can_manage_admin(),
                    "can_manage_employee": user.can_manage_employee(),
                    "can_manage_enquiry": user.can_manage_enquiry(),
                    "can_access_django_admin": user.can_access_django_admin(),
                }
            }
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


# ==================== ADMIN CRUD APIs ====================

class AdminRegisterAPIView(APIView):
    """
    Admin CRUD - Admin aur Superuser DONO kar sakte hain
    """
    permission_classes = [IsAuthenticated, CanManageAdmin]

    def get(self, request, pk=None):
        """Get Admins"""
        if pk:
            try:
                admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
                serializer = AdminSerializer(admin)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        
        admins = User.objects.filter(is_admin=True, is_superuser=False).order_by('-created_at')
        serializer = AdminSerializer(admins, many=True)
        return Response({
            "count": admins.count(),
            "admins": serializer.data
        })

    def post(self, request):
        """Create Admin - Admin aur Superuser dono"""
        serializer = AdminSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            admin = serializer.save()
            return Response({
                "message": "Admin successfully create ho gaya",
                "admin": AdminSerializer(admin).data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Update Admin"""
        try:
            admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
            serializer = AdminSerializer(admin, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Admin successfully update ho gaya",
                    "admin": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """Delete Admin"""
        try:
            admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
            
            # Admin apne aap ko delete nahi kar sakta
            if admin.id == request.user.id:
                return Response(
                    {"error": "Aap apne aap ko delete nahi kar sakte"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            admin_email = admin.email
            admin.delete()
            return Response({
                "message": f"Admin '{admin_email}' successfully delete ho gaya"
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)


# ==================== EMPLOYEE CRUD APIs ====================

class EmployeeAPIView(APIView):
    """
    Employee CRUD - Admin aur Superuser dono
    """
    permission_classes = [IsAuthenticated, CanManageEmployee]

    def get(self, request, pk=None):
        if pk:
            try:
                employee = Employee.objects.get(pk=pk)
                serializer = EmployeeSerializer(employee)
                return Response(serializer.data)
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        employees = Employee.objects.all().order_by('-created_at')
        serializer = EmployeeSerializer(employees, many=True)
        return Response({
            "count": employees.count(),
            "employees": serializer.data
        })

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            employee = serializer.save()
            return Response({
                "message": "Employee successfully create ho gaya",
                "employee": EmployeeSerializer(employee).data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = EmployeeSerializer(employee, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Employee successfully update ho gaya",
                    "employee": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            employee_name = employee.name
            employee.delete()
            return Response({
                "message": f"Employee '{employee_name}' successfully delete ho gaya"
            }, status=status.HTTP_200_OK)
            
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)


# ==================== ENQUIRY CRUD APIs ====================

class EnquiryAPIView(APIView):
    """
    Enquiry CRUD
    - POST: Public
    - GET/PATCH/DELETE: Admin & Superuser
    """
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated(), CanManageEnquiry()]

    def get(self, request, pk=None):
        if pk:
            try:
                enquiry = Enquiry.objects.get(pk=pk)
                serializer = EnquirySerializer(enquiry)
                return Response(serializer.data)
            except Enquiry.DoesNotExist:
                return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)

        enquiries = Enquiry.objects.all().order_by('-created_at')
        serializer = EnquirySerializer(enquiries, many=True)
        return Response({
            "count": enquiries.count(),
            "enquiries": serializer.data
        })

    def post(self, request):
        serializer = EnquirySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Enquiry successfully submit ho gayi",
                "enquiry": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            enquiry = Enquiry.objects.get(pk=pk)
            serializer = EnquirySerializer(enquiry, data=request.data, partial=True)
            
            if serializer.is_valid():
                enquiry = serializer.save()
                if request.user.is_authenticated:
                    enquiry.handled_by = request.user
                    enquiry.save()
                    
                return Response({
                    "message": "Enquiry successfully update ho gayi",
                    "enquiry": EnquirySerializer(enquiry).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Enquiry.DoesNotExist:
            return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            enquiry = Enquiry.objects.get(pk=pk)
            enquiry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Enquiry.DoesNotExist:
            return Response({"error": "Enquiry not found"}, status=status.HTTP_404_NOT_FOUND)     



# ==================== DASHBOARD & PROFILE ====================

class DashboardAPIView(APIView):

    def get_monthly_chart_data(self):
        # --- Enquiry count grouped by month ---
        enquiry_qs = (
            Enquiry.objects
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(enquiries=Count("id"))
            .order_by("month")
        )

        # --- Employee count grouped by month ---
        employee_qs = (
            Employee.objects
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(employees=Count("id"))
            .order_by("month")
        )

        enquiries_map = {r["month"]: r["enquiries"] for r in enquiry_qs}
        employees_map = {r["month"]: r["employees"] for r in employee_qs}

        months = sorted(set(enquiries_map.keys()) | set(employees_map.keys()))

        data = []
        for m in months:
            data.append({
                "month": month_abbr[m.month],          # Jan / Feb / Mar
                "employees": employees_map.get(m, 0),
                "enquiries": enquiries_map.get(m, 0),
            })

        return data


    def get(self, request):
        return Response({
            "total_admin": User.objects.filter(is_admin=True).count(),
            "total_employee": Employee.objects.count(),
            "today_enquiry": Enquiry.objects.filter(
                created_at__date=now().date()
            ).count(),
            "total_enquiry": Enquiry.objects.count(),

            # 🔹 Monthly chart data (FE chart uses this)
            "enquiries_by_month": self.get_monthly_chart_data(),
        })

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile successfully update ho gaya",
                "user": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CareerAPIView(APIView):
    """
    GET  -> Public
    POST/PATCH/DELETE -> Admin + Superuser
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrSuperUser()]

    def get(self, request):
        careers = Career.objects.filter(is_active=True)
        serializer = CareerSerializer(careers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CareerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        career = Career.objects.get(pk=pk)
        serializer = CareerSerializer(career, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        Career.objects.filter(pk=pk).delete()
        return Response(status=204)


class JobApplicationAPIView(APIView):
    """
    POST -> Public
    GET / DELETE -> Admin + Superuser
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrSuperUser()]

    def post(self, request):
        serializer = JobApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Application submitted successfully"},
                status=201
            )
        return Response(serializer.errors, status=400)

    def get(self, request):
        applications = JobApplication.objects.all().order_by("-created_at")
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        JobApplication.objects.filter(pk=pk).delete()
        return Response(status=204)
