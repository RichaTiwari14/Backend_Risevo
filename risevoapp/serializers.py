from rest_framework import serializers
from .models import *

class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'contact_no', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']

    def create(self, validated_data):
        """
        Dashboard se admin create - Sirf dashboard access, Django admin nahi
        """
        request = self.context.get('request')
        
        user = User.objects.create_admin(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            contact_no=validated_data.get("contact_no", ""),
        )
        
        # Track who created this admin
        if request and request.user.is_authenticated:
            user.created_by = request.user
            user.save()
            
        return user

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.contact_no = validated_data.get('contact_no', instance.contact_no)
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'address', 'designation', 'contact_no', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        
        employee = Employee.objects.create(**validated_data)
        
        if request and request.user.is_authenticated:
            employee.created_by = request.user
            employee.save()
            
        return employee


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'contact_no', 'role', 'is_superuser', 'is_admin']