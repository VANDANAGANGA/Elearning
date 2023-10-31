import re
import phonenumbers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from phonenumber_field.serializerfields import PhoneNumberField
from.models import UserAccount
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True) 
    class Meta:
        model = UserAccount
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
        user = UserAccount.objects.create(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            role=validated_data['role']
           
        )
        user.set_password(validated_data['password'])
        print(user)
        user.save()
        
        return user
