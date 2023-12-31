from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import UserRegistrationSerializer,CourseCategorySerializer,TeacherSerializer,CourseSerializer,StudentSerializer,TeacherCourseSerializer,ModuleSerializer,ChapterSerializer
from.models import UserAccount,CourseCategory,Course,TeacherProfile,StudentProfile,Module,Chapter
import random
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser




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
            print(otp,555555555555555555555555555555555)
            # Send the OTP to the user's email
            # send_mail('OTP Verification', f'Your OTP is: {otp}', 'vandu.ganga96@gmail.com', [email])
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


class UserRegister(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        print(request.data,1111111111111111111111111111111111111111111111) 
        serializer = UserRegistrationSerializer(data=request.data)
        print(serializer,77777777777777777777777777777777777)
        if serializer.is_valid():
            print(222222222222222222222222222222222222222222222222)
            user = serializer.save()
            print(user) # Save the user to the database
            return Response({"message": "User registration successful."}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
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


        if user.role == 3:
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
                token['role_id'] = teacher_profile.id
                # Add other teacher profile data as needed
            except TeacherProfile.DoesNotExist:
                token['role_id'] = None
        elif user.role == 2:
            try:
                student_profile = StudentProfile.objects.get(user=user)
                token['role_id'] = student_profile.id
                # Add other student profile data as needed
            except StudentProfile.DoesNotExist:
                token['role_id'] = None
        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer 


class MyTokenLogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logout successful.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)    
#<--------------------------------------------------------------------------------------------------------------------------------------------------->
class CourseCategoryView(APIView):
    def post(self,request):
        serializer=CourseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request):
        categories = CourseCategory.objects.all()
        serializer=CourseCategorySerializer(categories,many=True)
        return Response(serializer.data)
#<-------------------------------------------------------------------------------------------------------------------->
class TeacherListView(APIView):
    def get(self, request):
        teachers = TeacherProfile.objects.all()
        print(teachers)
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        try:
            teacher_id = request.data.get('id')

            if teacher_id is not None:
                teacher = UserAccount.objects.get(id=teacher_id)
                # Toggle the is_active field
                teacher.is_active = not teacher.is_active
                teacher.save()
                return Response({'detail': 'Teacher updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)
#<------------------------------------------------------------------------------------------------------------------------>                 
class StudentListView(APIView):
    def get(self, request):
        students = StudentProfile.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        try:
            student_id = request.data.get('id')

            if student_id is not None:
                teacher = UserAccount.objects.get(id=student_id)
                # Toggle the is_active field
                teacher.is_active = not teacher.is_active
                teacher.save()
                return Response({'detail': 'Student updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
#<--------------------------------------------------------------------------------------------------------------------------------------->
class CourseView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
#<----------------------------------------------------------------------------------------------------------->
class TeacherCourse(APIView):
    def get(self,request):
        try:
            teacher_id = request.query_params.get('id')
            print(teacher_id,888888888888888888888888)
            if teacher_id is not None:
                courses=Course.objects.filter(teacher=teacher_id)
                serializer=TeacherCourseSerializer(courses,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)    
#<-------------------------------------------------------------------------------------------------------------------->
class CourseDetailView(APIView):
    def get(self,request):
        try: 
            course_id = request.query_params.get('id')
            print(course_id)
            if course_id is not None:
                course = Course.objects.get(id=course_id)
                serializer = CourseSerializer(course)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)     
#<------------------------------------------------------------------------------------------------------------------>
# class ModulesAndChapters(APIView):
#      def get(self,request):
#         try:
#             course_id = request.query_params.get('id')
#             print(course_id,888888888888888888888888)
#             course = Course.objects.get(id=course_id)
#         except Course.DoesNotExist:
#             return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

#         modules = Module.objects.filter(course=course)
#         module_data = []

#         for module in modules:
#             module_serializer = ModuleSerializer(module)
#             chapter_queryset = Chapter.objects.filter(module=module)
#             chapter_serializer = ChapterSerializer(chapter_queryset, many=True)
#             module_data.append({
#                 'module': module_serializer.data,
#                 'chapters': chapter_serializer.data
#             })

#         return Response(module_data, status=status.HTTP_200_OK)
    
class ModuleView(APIView): 
    def get(self,request):
        try:
            course_id = request.query_params.get('id')
            print(course_id,888888888888888888888888)
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        modules = Module.objects.filter(course=course)
        module_data = []

        for module in modules:
            module_serializer = ModuleSerializer(module)
            chapter_queryset = Chapter.objects.filter(module=module)
            chapter_serializer = ChapterSerializer(chapter_queryset, many=True)
            module_data.append({
                'module': module_serializer.data,
                'chapters': chapter_serializer.data
            })

        return Response(module_data, status=status.HTTP_200_OK)
    
   
    def post(self, request, *args, **kwargs):
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChapterView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = ChapterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   