import re
import phonenumbers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from phonenumber_field.serializerfields import PhoneNumberField
from.models import UserAccount,CourseCategory,Course,TeacherProfile,StudentProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True) 
    class Meta:
        model = User
        fields = ['email','password', 'password2','full_name','phone_number','role']  # Include password2 field in fields

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        

        phone_number = attrs.get('phone_number', None)
        phone_number_pattern = r'^\+\d{1,3}\s?\d{3,14}$'

        if phone_number:
           if not re.match(phone_number_pattern, phone_number):
                raise serializers.ValidationError({"phone_number": "Invalid phone number format."})
        role = attrs.get('role')
        if role:
        # Check if the provided role is an integer, and if not, map it to the corresponding integer.
            role_mapping = {
            '1': 1,  # ADMIN
            '2': 2,  # STUDENT
            '3': 3,  # TEACHER
            }
            attrs['role'] = role_mapping.get(str(role), role)

        return attrs
    def create(self, validated_data):
        role = validated_data['role'] 
        user = User.objects.create(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            role=validated_data['role']
           
        )
        user.set_password(validated_data['password'])
        print(user)
        user.save()
        if role == 3:  # Assuming '3' is the role code for TEACHER
            TeacherProfile.objects.create(
                user=user,
                years_of_experience=validated_data.get('years_of_experience', 0),
                experience=validated_data.get('experience', ''),
                about=validated_data.get('about', '')
            )
        if role == 2:  # Assuming '3' is the role code for TEACHER
            StudentProfile.objects.create(
                user=user,
                hightest_education=validated_data.get('years_of_experience', 0),
                experience=validated_data.get('experience', ''),
                about=validated_data.get('about', '')
            )    

        return user
#<----------------------------------------------------------------------------------------------------------------->
class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = '__all__'
#<-------------------------------------------------------------------------------------------------------------------->

class TeacherSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number=serializers.CharField(source='user.phone_number',read_only=True)
    is_active = serializers.BooleanField(source='user.is_active')
    profile_pic=serializers.ImageField(source='user.profile_pic')
    
    class Meta:
        model = TeacherProfile
        fields = ['user_id','full_name','email','phone_number','profile_pic','is_active','years_of_experience','experience','about']      

#<---------------------------------------------------------------------------------------------------------------------->
class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number=serializers.CharField(source='user.phone_number',read_only=True)
    is_active = serializers.BooleanField(source='user.is_active')
    profile_pic=serializers.ImageField(source='user.profile_pic')
    class Meta:
        model=UserAccount
        fields=['full_name','email','phone_number','profile_pic','is_active']
#<-------------------------------------------------------------------------------------------------------------->
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'teacher', 'category', 'is_active', 'start_date', 'end_date', 'price']