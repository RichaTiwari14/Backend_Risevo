from rest_framework import serializers
from .models import User, Employee, Enquiry , Career, JobApplication


class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=False)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'password', 'contact_no', 
            'role', 'is_active', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'role', 'created_at', 'created_by_name']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.name or obj.created_by.email
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        
        user = User.objects.create_admin(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            contact_no=validated_data.get("contact_no", ""),
        )
        
        if request and request.user.is_authenticated:
            user.created_by = request.user
            user.save()
            
        return user

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.contact_no = validated_data.get('contact_no', instance.contact_no)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance


class EmployeeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'email', 'address', 'designation', 
            'contact_no', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_name']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.name or obj.created_by.email
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        employee = Employee.objects.create(**validated_data)
        
        if request and request.user.is_authenticated:
            employee.created_by = request.user
            employee.save()
            
        return employee


class EnquirySerializer(serializers.ModelSerializer):
    handled_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 
            'message', 'status', 'handled_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'handled_by_name']

    def get_handled_by_name(self, obj):
        if obj.handled_by:
            return obj.handled_by.name or obj.handled_by.email
        return None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'contact_no', 'role', 
            'is_superuser', 'is_admin', 'permissions'
        ]
        read_only_fields = ['id', 'role', 'is_superuser', 'is_admin']

    def get_permissions(self, obj):
        return {
            'can_manage_admin': obj.can_manage_admin(),
            'can_manage_employee': obj.can_manage_employee(),
            'can_manage_enquiry': obj.can_manage_enquiry(),
            'can_access_dashboard': obj.can_access_dashboard(),
            'can_access_django_admin': obj.can_access_django_admin(),
        }
    
class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = "__all__"


class JobApplicationSerializer(serializers.ModelSerializer):
    career_title = serializers.CharField(
        source="career.designation",
        read_only=True
    )

    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = ["created_at"]
