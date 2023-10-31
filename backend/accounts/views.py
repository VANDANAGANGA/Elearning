from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import UserRegistrationSerializer
from.models import UserAccount
import random
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



#<------------------------------------------------Registration Start------------------------------------------------------------------------------>
otp_storage = {}
class GenerateOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        print(email,1111111111111111111111111)
        if email:
            if UserAccount.objects.filter(email=email).exists():
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            otp_storage[email] = otp 
            # Send the OTP to the user's email
            send_mail('OTP Verification', f'Your OTP is: {otp}', 'vandu.ganga96@gmail.com', [email])
            print(777777777777777)
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        entered_otp = request.data.get('otp')

        if email in otp_storage:
            stored_otp = otp_storage[email]
            if entered_otp == stored_otp:
                del otp_storage[email]  # Remove the OTP from the dictionary
                return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'OTP verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# class StudentListAPIView(APIView):
#     def get(self, request):
#         students = UserAccount.objects.filter(is_student=True)
#         serializer = StudentAccountSerializer(students, many=True)
#         return Response(serializer.data)
class UserRegister(APIView):
    def post(self, request):
        print(request.data,1111111111111111111111111111111111111111111111) 
        serializer = UserRegistrationSerializer(data=request.data)
        print(serializer,77777777777777777777777777777777777)
        if serializer.is_valid():
            print(222222222222222222222222222222222222222222222222)
            user = serializer.save()
            print(user) # Save the user to the database
            return Response({"message": "User registration successful."}, status=status.HTTP_201_CREATED)
        print(123456789)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        users = UserAccount.objects.all()
        serializer = UserRegistrationSerializer(users, many=True)
        return Response(serializer.data)
#<----------------------------------------------------Registration End ------------------------------------------>
# <--------------------------------------------------Login Start ------------------------------------------------->
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        print(user,6666666666666666666666666)
        token = super().get_token(user)
        token['full_name'] = user.full_name
        token['is_superuser'] = user.is_superuser
        token['role']= user.role
        token['email'] = user.email
        token['phonenumber'] = user.phone_number
        return token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer 