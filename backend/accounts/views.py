from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import UserRegistrationSerializer,CourseCategorySerializer,TeacherSerializer,CourseSerializer,StudentSerializer,TeacherCourseSerializer,ModuleSerializer,ChapterSerializer,AssignmentSerializer,QuizSerializer,QuestionSerializer,OrderSerializer,StudentCourseSerializer,StudentAssignmentSerializer,StudentQuizSerializer,MasterclassSerializer,SheduleSerializer,RoomSerializer,MessageSerializer,StudentQuizsSerializer,StudentChapterSerializer,StudentCertificateSerializer
from.models import UserAccount,CourseCategory,Course,TeacherProfile,StudentProfile,Module,Chapter,Assignment,Quiz,Questions,Order,StudentCourse,StudentAssignment,StudentQuiz,Masterclass,Shedule,Room,Message,StudentChapter,StudentCertificate
import random
from .serializers import TeacherProfileSerializer,UserSerializer,StudentProfileSerializer,ProfilePicSerializer
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
import razorpay
from backend.settings import RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET
import base64
from django.db.models import Sum,Count
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated







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
class ProfilePic(APIView):
    def get(self, request):
        try:
            id = request.query_params.get('id')
            user = UserAccount.objects.get(id=id)
            serializer = ProfilePicSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#<------------------------------------------------------------------------------------------------------------------------------------------------------------>        
class CourseCategoryView(APIView):
    def post(self,request):
        serializer=CourseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def get(self,request):
        categories = CourseCategory.objects.all()
        category_data = []
        for category in categories:
            num_courses = Course.objects.filter(category=category).count()
            serializer=CourseCategorySerializer(category)
            category_data.append({
                **serializer.data,
                'num_courses': num_courses
            })
        return Response(category_data)
    def delete(self, request,):
        try:
            category_id = request.query_params.get('id')
            category = CourseCategory.objects.get(pk=category_id)
        except CourseCategory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
#<-------------------------------------------------------------------------------------------------------------------->
class CourseView(APIView):
    @staticmethod
    def get_category_name(category_id):
        try:
            category = CourseCategory.objects.get(id=category_id)
            return category.icon_url
        except CourseCategory.DoesNotExist:
            return None

    @staticmethod
    def get_teacher_name(teacher_id):
        try:
            teacher = TeacherProfile.objects.get(id=teacher_id)
            return teacher.user.full_name
        except TeacherProfile.DoesNotExist:
            return None
    def get(self, request):
        courses = Course.objects.filter(is_active=True)
        course_data = []

        for course in courses:
            serialized_course = CourseSerializer(course).data
            category_icon = self.get_category_name(course.category.id)
            teacher_name = self.get_teacher_name(course.teacher.id)
            print(8888888888888888888888888888888888888888)
            serialized_course['category'] = category_icon
            serialized_course['teacher'] = teacher_name

            course_data.append(serialized_course)
            
        return Response(course_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      
    def delete(self,request,*arg, **kwargs):
        try:
            course_id = request.query_params.get('id')
            if course_id is not None:
                module=Course.objects.get(id=course_id)
                module.delete()
                return Response({"message": "Course deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Course ID not provided in query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)    
#<------------------------------------------------------------------------------------------------------------------------------->
class CourseDetailsAPIView(APIView):
    def get(self,request):
        try:
            course_id = request.query_params.get('id')
            print(course_id,888888888888888888888888)
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        course_serializer = CourseSerializer(course)
        teacher_serializer = TeacherSerializer(course.teacher)
        modules = Module.objects.filter(course=course)
        assignments = Assignment.objects.filter(course=course)
        quizzes = Quiz.objects.filter(course=course)
        module_data = []

        for module in modules:
            module_serializer = ModuleSerializer(module)
            chapter_queryset = Chapter.objects.filter(module=module)
            chapter_serializer = ChapterSerializer(chapter_queryset, many=True)
            module_data.append({
                'module': module_serializer.data,
                'chapters': chapter_serializer.data
            })
            response_data = {
            'course': course_serializer.data,
            'teacher':teacher_serializer.data,
            'modules': module_data,
            'num_assignments': assignments.count(),
            'num_quizzes': quizzes.count(),
        }

        return Response(response_data, status=status.HTTP_200_OK)
#<------------------------------------------------------------------------------------------------------------------------------> 
class TeamListView(APIView):
    def get(self,request):
        team= TeacherProfile.objects.filter(user__is_active=True)
        team_serializer = TeacherSerializer(team,many=True)
        return Response(team_serializer.data, status=status.HTTP_200_OK)
#<---------------------------------------------------------------------------------------------------------------------------------------->
class AboutView(APIView):
     def get(self,request):      
        total_teachers = UserAccount.objects.filter(role=UserAccount.TEACHER).count()
        total_students = UserAccount.objects.filter(role=UserAccount.STUDENT).count()
        total_courses=Course.objects.all().count()
        print(77777777777777777777777777777777777777777777777777777777777)
        return Response({
                'total_teachers': total_teachers,
                'total_students': total_students,
                'total_course': total_courses,
                
            })
#<----------------------------------------------------------------------------------------------------------->
class ContactFormView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        subject = request.data.get('subject')
        message = request.data.get('message')
      
        try:
            send_mail(
                subject,
                f"Name: {name}\nEmail: {email}\n\nMessage: {message}",
                'vandu.ganga96@gmail.com',
                ['vandu.ganga96@gmail.com'],
                fail_silently=False,
            )
            return Response({'message': 'Email sent successfully'}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)    
#<------------------------------------------------------------------------------------------------------------------------------------>
                                              # Admin View
#<---------------------------------------------------------------------------------------------------------------------------->
class TeacherListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        teachers = TeacherProfile.objects.all()
        teacher_data = []
        for teacher in teachers:
            teacher_serializer = TeacherSerializer(teacher)
            courses = Course.objects.filter(teacher=teacher)
            course_data = []
            for course in courses:
                course_serializer = CourseSerializer(course)
                category_name = course.category.title if course.category else None
                course_data.append({
                    'course': course_serializer.data,
                    'category_name': category_name
                })
            teacher_data.append({
                'teacher': teacher_serializer.data,
                'courses': course_data
            })
        return Response(teacher_data, status=status.HTTP_200_OK)
       
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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        students = StudentProfile.objects.all()
        student_data=[]
        for student in students:
          serializer = StudentSerializer(student)
          enrolled_courses = StudentCourse.objects.filter(student=student)
          enrolled_courses_data = []
          for enrolled_course in enrolled_courses:
                course = enrolled_course.course
                course_data = CourseSerializer(course).data
                course_data['enrolled_at'] = enrolled_course.enrolled_at.date()
                course_data['category_name'] = course.category.title
                enrolled_courses_data.append(course_data)
          student_data.append({
                'student': serializer.data,
                'enrolled_courses': enrolled_courses_data
            })
          
        return Response(student_data, status=status.HTTP_200_OK)
    
    def put(self, request):
        try:
            student_id = request.data.get('id')
            print(student_id)
            if student_id is not None:
                student = UserAccount.objects.get(id=student_id)
                student.is_active = not student.is_active
                print(8888888888888888888888888888888888888888888888888)
                student.save()
                return Response({'detail': 'Student updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
#<--------------------------------------------------------------------------------------------------------------------->
class AdminCourse(APIView):     
     permission_classes = [IsAuthenticated]
     def get(self, request):
        course = Course.objects.all()
        serializer = CourseSerializer(course, many=True)
        modified_data = []
        for course_data in serializer.data:
            teacher_id = course_data.get('teacher') 
            if teacher_id is not None:
                try:
                    teacher = TeacherProfile.objects.select_related('user').get(id=teacher_id)
                    course_data['teacher_name'] = teacher.user.full_name
                    if teacher.user.profile_pic:
                        encoded_image = base64.b64encode(teacher.user.profile_pic.read()).decode('utf-8')
                        course_data['profile_pic'] = encoded_image
                    else:
                        course_data['profile_pic'] = None
                except TeacherProfile.DoesNotExist:
                    course_data['teacher_name'] = None
            category_id=course_data.get('category')
            if category_id is not None:
                try:
                    category = CourseCategory.objects.get(id=category_id)
                    course_data['category_url'] = category.icon_url
                except CourseCategory.DoesNotExist:
                    course_data['category_url'] = None
            course_id = course_data.get('id')
            if course_id is not None:
                students_enrolled = StudentCourse.objects.filter(course=course_id).count()
                course_data['students_enrolled'] = students_enrolled
        
            modified_data.append(course_data)
            print(modified_data)
        return Response(modified_data, status=status.HTTP_200_OK)
     def put(self, request):
        try:
            course_id = request.data.get('id')
            print(course_id)
            if course_id is not None:
                course = Course.objects.get(id=course_id)
                course.is_active = not course.is_active
                print(8888888888888888888888888888888888888888888888888)
                course.save()
                return Response({'detail': 'Course updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
#<---------------------------------------------------------------------------------------------------------------------------------------------->
class AdminCourseDetails(APIView): 
     permission_classes = [IsAuthenticated] 
     def get(self,request):
        try: 
            course_id = request.query_params.get('id')
            print(course_id)
            if course_id is not None:
                course = Course.objects.get(id=course_id)
                course_serializer = CourseSerializer(course)
                modules = Module.objects.filter(course=course)
                modules_data = []
                for module in modules:
                    module_serializer = ModuleSerializer(module)
                    chapters = Chapter.objects.filter(module=module)
                    chapters_data = []
                    for chapter in chapters:
                        chapter_serializer = ChapterSerializer(chapter)
                        chapters_data.append(chapter_serializer.data)
                    module_data = {
                        **module_serializer.data,
                        'chapters': chapters_data
                    }
                    modules_data.append(module_data)
                
                teacher = course.teacher
                teacher_serializer = TeacherSerializer(teacher)

                students = course.student_set.all()
                students_data = []
                for student in students:
                    student_serializer = StudentSerializer(student)
                    students_data.append(student_serializer.data)

                serialized_data = {
                    **course_serializer.data,
                    'modules': modules_data,
                    'teacher': teacher_serializer.data,
                    'students': students_data
                }
                return Response(serialized_data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
#<------------------------------------------------------------------------------------------------------------------------------------------------------->
class DashBoard(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        total_teachers = UserAccount.objects.filter(role=UserAccount.TEACHER).count()
        total_students = UserAccount.objects.filter(role=UserAccount.STUDENT).count()
        total_order_amount = Order.objects.aggregate(total_amount=Sum('order_amount'))['total_amount']
        courses_with_enrollment_count = Course.objects.annotate(num_students=Count('studentcourse'))

        # Serialize the queryset to return in the response
        serialized_data = []
        for course in courses_with_enrollment_count:
            serialized_data.append({
                'title': course.title,
                'num_students_enrolled': course.num_students,
            })
        # You may need to serialize the data before returning it
        total_teachers_data = {'total_teachers': total_teachers}
        total_students_data = {'total_students': total_students}
        total_order_amount_data = {'total_order_amount': total_order_amount}
        courses_data = CourseSerializer(courses_with_enrollment_count, many=True).data

        return Response({
            'total_teachers': total_teachers_data,
            'total_students': total_students_data,
            'total_order_amount': total_order_amount_data,
            'courses_with_enrollment_count': serialized_data
        })
#<-------------------------------------------------------------------------------------------------------------------->
class SalesReport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        orders = Order.objects.all()
        sales_data = []

        for order in orders:
            sales_data.append({
                'id': order.id,
                'student_name': order.student.user.full_name,  # Access the student's name directly
                'order_amount': order.order_amount,
                'order_payment_id': order.order_payment_id,
                'is_active': order.is_active,
                'order_date': order.order_date,
                'months': order.months
            })

        return Response(sales_data)
#<--------------------------------------------------------------------------------------------------------------------------------------->
#<-------------------------------------------------------------------------------------------------------------------------------------------->       

              
#<----------------------------------------------------------------------------------------------------------->
                 # Teacher Views
#<------------------------------------------------------------------------------------------------------------->
class TeacherCourse(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            teacher_id = request.query_params.get('id')
            print(teacher_id, 888888888888888888888888)
            if teacher_id is not None:
                courses = Course.objects.filter(teacher=teacher_id)
                serialized_courses = []
                for course in courses:
                    # Calculate the count of students enrolled in each course
                    num_students_enrolled = course.studentcourse_set.count()
                    
                    # Include the count in the serialized data
                    serialized_data = TeacherCourseSerializer(course).data
                    serialized_data['num_students_enrolled'] = num_students_enrolled

                    serialized_courses.append(serialized_data)

                return Response(serialized_courses, status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)
#<-------------------------------------------------------------------------------------------------------------------->
class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try: 
            course_id = request.query_params.get('id')
            print(course_id)
            if course_id is not None:
                course = Course.objects.get(id=course_id)
                serializer = CourseSerializer(course)
                modules = Module.objects.filter(course=course)
                assignments = Assignment.objects.filter(course=course)
                quizzes = Quiz.objects.filter(course=course)
                serialized_data = {
                    **serializer.data,
                    'num_modules': modules.count(),
                    'num_assignments': assignments.count(),
                    'num_quizzes': quizzes.count(),
                }
                print(serialized_data,88888888888888888888888888888888888888888888)
                return Response(serialized_data,status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)     
#<------------------------------------------------------------------------------------------------------------------>
class ModuleView(APIView): 
    permission_classes = [IsAuthenticated]
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
    def delete(self,request,*arg, **kwargs):
        try:
            module_id = request.query_params.get('id')
            if module_id is not None:
                module=Module.objects.get(id=module_id)
                module.delete()
                return Response({"message": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Module ID not provided in query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Module not found"}, status=status.HTTP_404_NOT_FOUND)
            


#<---------------------------------------------------------------------------------------------------------------------->
class ChapterView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = ChapterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    def delete(self,request,*arg, **kwargs):
        try:
            chapter_id = request.query_params.get('id')
            if chapter_id is not None:
                chapter=Chapter.objects.get(id=chapter_id)
                chapter.delete()
                return Response({"message": "Chapter deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Chapter ID not provided in query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Chapter not found"}, status=status.HTTP_404_NOT_FOUND)
            
#<-------------------------------------------------------------------------------------------------------------->
class TeacherAssignemnt(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request):
        try:
            course_id = request.query_params.get('id')
            print(course_id)
            if course_id is not None:
                assignments = Assignment.objects.filter(course=course_id)
                assignment_details = []

                for assignment in assignments:
                    student_assignments = assignment.studentassignment_set.all()
                    assignment_data = AssignmentSerializer(assignment).data
                    student_assignment_data = StudentAssignmentSerializer(student_assignments, many=True).data

                    assignment_details.append({
                        'assignment': assignment_data,
                        'students': student_assignment_data,
                    })

                return Response(assignment_details, status=status.HTTP_200_OK)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)    
    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,*arg, **kwargs):
        try:
            assignment_id = request.query_params.get('id')
            if assignment_id is not None:
                assignment=Assignment.objects.get(id=assignment_id)
                assignment.delete()
                return Response({"message": "Assignment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Assignment ID not provided in query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)
#<--------------------------------------------------------------------------------------->    
class TeacherQuiz(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            course_id=request.query_params.get('id')
            if course_id is not None:
                quiz=Quiz.objects.filter(course=course_id)
                quiz_data = []
                for quiz in quiz:
                    quiz_questions = Questions.objects.filter(quiz=quiz)
                    quiz_details=QuizSerializer(quiz).data
                    question_serializer = QuestionSerializer(quiz_questions, many=True)
                    student_quiz = quiz.studentquiz_set.all()
                    student_quiz_data = StudentQuizSerializer(student_quiz, many=True).data

                    quiz_data.append({
                        'quiz': quiz_details,
                        'questions': question_serializer.data,
                        'students': student_quiz_data,
                    })
                return Response(quiz_data,status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz  not found'}, status=status.HTTP_404_NOT_FOUND)  
    def post(self,request):
        print(request.data)
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,*arg, **kwargs):
        try:
            quiz_id = request.query_params.get('id')
            if quiz_id is not None:
                quiz=Quiz.objects.get(id=quiz_id)
                quiz.delete()
                return Response({"message": "Quiz deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Quiz ID not provided in query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
#<--------------------------------------------------------------------------------------------------------->
class TeacherQuestions(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            quiz_id=request.query_params.get('id')
            if quiz_id is not None:
                quiz=Questions.objects.filter(quiz=quiz_id)
                serializer=QuestionSerializer(quiz,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except Questions.DoesNotExist:
            return Response({'error': 'Questions  not found'}, status=status.HTTP_404_NOT_FOUND)  
    def post(self,request):
        print(request.data)
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,*arg, **kwargs):
        try:
            question_id = request.query_params.get('id')
            if question_id is not None:
                question=Questions.objects.get(id=question_id)
                question.delete()
                return Response({"message": "Question deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Question ID not provided in query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
#<---------------------------------------------------------------------------------------------------------------------->
class TeacherAllAssignment(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            teacher_id = request.query_params.get('id')
            print(teacher_id,888888888888888888888888)
            if teacher_id is not None:
                courses = Course.objects.filter(teacher=teacher_id)
                serialized_data = []

                for course in courses:
                    assignments = Assignment.objects.filter(course=course)
                    course_data = CourseSerializer(course).data
                    assignment_details = []

                    for assignment in assignments:
                        student_assignments = StudentAssignment.objects.filter(assignment=assignment)
                        assignment_data = AssignmentSerializer(assignment).data
                        student_assignment_data = StudentAssignmentSerializer(student_assignments, many=True).data
                        assignment_details.append({
                            'assignment': assignment_data,
                            'students': student_assignment_data
                        })

                    
                    # Append course data along with assignments to the serialized_data list
                    serialized_data.append({
                        'course': course_data,
                        'assignments': assignment_details
                    })
                
                return Response(serialized_data, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
                return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Course ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
# <----------------------------------------------------------------------------------------------------------------------->
class TeacherAllQuiz(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            teacher_id = request.query_params.get('id')
            print(teacher_id,888888888888888888888888)
            if teacher_id is not None:
                courses = Course.objects.filter(teacher=teacher_id)
                serialized_data = []

                for course in courses:
                    quizs = Quiz.objects.filter(course=course)
                    course_data = CourseSerializer(course).data
                    quiz_details = []

                    for quiz in quizs:
                        student_quiz = quiz.studentquiz_set.all()
                        student_quiz_data = StudentQuizSerializer(student_quiz, many=True).data
                        quiz_data = QuizSerializer(quiz).data
                        quiz_questions = Questions.objects.filter(quiz=quiz)
                        question_serializer = QuestionSerializer(quiz_questions, many=True)
                        quiz_details.append({
                            'quiz': quiz_data,
                            'students': student_quiz_data,
                            'questions': question_serializer.data,
                        })

                    
                    # Append course data along with assignments to the serialized_data list
                    serialized_data.append({
                        'course': course_data,
                        'quiz': quiz_details
                    })
                
                return Response(serialized_data, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
                return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Course ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
#<---------------------------------------------------------------------------------------------------------------------->    
class TeacherProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if teacher_id is not None:
            try:
                teacher = TeacherProfile.objects.get(id=teacher_id)
                serializer = TeacherSerializer(teacher)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TeacherProfile.DoesNotExist:
                return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST) 
    def put(self, request):
        teacher_id = request.data.get('teacher_id')
        user_id = request.data.get('user_id')
        print(request.data)
        try:
            user=UserAccount.objects.get(id=user_id)
            teacher = TeacherProfile.objects.get(id=teacher_id)
        except TeacherProfile.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user_serializer = UserSerializer(user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
        serializer = TeacherProfileSerializer(teacher, data=request.data, partial=True)
        print(8888888888888888888888888888888888888888888888)
        if serializer.is_valid():
            print(888888888888888888888888888888888)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#<----------------------------------------------------------------------------------------------------------------->
class SheduleApiView(APIView):    
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            teacher_id = request.query_params.get('id')
            print(teacher_id,888888888888888888888888)
            if teacher_id is not None:
                shedule=Shedule.objects.filter(teacher=teacher_id)
                print(shedule)
                serializer=SheduleSerializer(shedule,many=True)
                print(serializer.data)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND) 
        
    def post(self, request):
        print(request.data,11111111111111111111111111111111111111111111111)
        serializer = SheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
    def put(self, request):
        try:
            shedule_id = request.query_params.get('id')
            print(shedule_id, 888888888888888888888888)
            if shedule_id is not None:
                shedule = Shedule.objects.get(id=shedule_id)
                shedule.completed = not shedule.completed
                shedule.save()
                serializer = SheduleSerializer(shedule)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Shedule id not provided.'}, status=status.HTTP_400_BAD_REQUEST)
        except Shedule.DoesNotExist:
            return Response({'detail': 'Shedule not found.'}, status=status.HTTP_404_NOT_FOUND)    
#<------------------------------------------------------------------------------------------------------------------------------------------------------>    
                         #Student Views
#<-------------------------------------------------------------------------------------------------------------------------------------->
class OrderApiView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        amount = request.data.get('amount')
        month = request.data.get('month')
        role = request.data.get('role_id')

        print(amount,role,month,8888888888888888888888888888888888888888888888888)
        try:
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            print(client,888888888888888888888888888888888888877777777777777777777777777)
            payment = client.order.create({"amount": int(amount) * 100, 
                                    "currency": "INR", 
                                    "payment_capture": "1"})
            print(role,3333333333333333333333333333333)
            student = StudentProfile.objects.get(id=int(role))
            active_order = Order.objects.filter(student=student, is_active=True).first()
            if active_order:
                if active_order.isValid():
                    return Response({'error': 'You already have an active plan'}, status=status.HTTP_400_BAD_REQUEST)
        except StudentProfile.DoesNotExist:
            print(f"StudentProfile with id={role} does not exist.")
            return Response({'error': 'StudentProfile not found for the given role_id'}, status=status.HTTP_404_NOT_FOUND)
        data={
            'student':student.id,  # Assuming the user is authenticated and has a related StudentProfile
            'order_amount': amount,
            'order_payment_id': payment['id'],
            'is_active': False,
            'months': month,
        }
        print(data,7777777777777777777777777777777777777777777777777777777777)
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'order':serializer.data,
                'razorpay_order': payment,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
class HandlePaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        ord_id = request.data.get('razorpay_order_id')
        try:
            order = Order.objects.get(order_payment_id=ord_id)
            order.is_active = True
            order.save()

            res_data = {
                'message': 'Payment successfully received!',
                'order_id': order.id
            }

            return Response(res_data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)   
#<---------------------------------------------------------------------------------------------------------->        
class CheckPayment(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            student_id = request.query_params.get('id')
            print(student_id, 888888888888888888888888) 
            if student_id is not None:
                valid_order_exists = Order.objects.filter(student=student_id, is_active=True).exists()
                print(999999999999999999999999999999999999999999999999999999999999999)
                if valid_order_exists:
                    return Response({"message": "Valid Plan exists for the student."}, status=status.HTTP_200_OK)
                else:
                    print(444444444444444444444444444444444444444444444)
                    return Response({"message": "No valid Plan exists for the student."}, status=200)
            else:
                return Response({"message": "Student ID is missing in query parameters."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#<-------------------------------------------------------------------------------------------------------------->         
class StudentCourseApiView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.data)
        serializer = StudentCourseSerializer(data=request.data)
        print(7777777777777777777777777777777777777777777777777)
        if serializer.is_valid():
            course_id = request.data.get('course')
            student_id = request.data.get('student')
            print(course_id,student_id)
            try:
                course = Course.objects.get(id=course_id)
                teacher = course.teacher
                room = Room.objects.get(course=course)
                
            except Course.DoesNotExist:
                return Response({"message": "Course does not exist."}, status=status.HTTP_404_NOT_FOUND)    
            if StudentCourse.objects.filter(student=student_id, course=course_id).exists():
                return Response({"message": "Student has already bought this course."},  status=200)
            else:
                room.students.add(student_id)
                teacher.account += 1000
                teacher.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    def get(self, request):
        try:
            student_id = request.query_params.get('id')
            print(student_id, 888888888888888888888888)
            if student_id is not None:
                courses = StudentCourse.objects.filter(student=student_id)
                serializer = StudentCourseSerializer(courses, many=True)
                print(serializer.data)
                courses_data = []
                for course in serializer.data:
                    course_id = course.get('course')
                    course_details=Course.objects.get(id=course_id)
                    courses_data.append({
                        'id': course_details.id,
                        'title': course_details.title,
                        'teacher_name': course_details.teacher.user.full_name if course_details.teacher else None,
                        # 'teacher_profile_pic': course_details.teacher.user.profile_pic if (course_details.teacher and course_details.teacher.user.profile_pic) else None,
                        'category_title': course_details.category.title if course_details.category else None,
                        'category_icon': course_details.category.icon_url if course_details.category else None,
                        'is_active': course_details.is_active,
                        'about': course_details.about,
                    })
                return Response(courses_data, status=status.HTTP_200_OK)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Missing "id" parameter'}, status=status.HTTP_400_BAD_REQUEST)
        except UserAccount.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
#<----------------------------------------------------------------------------------------------------------->
class StudentCourseDetails(APIView):
     permission_classes = [IsAuthenticated]
     def get(self,request):
        try: 
            course_id = request.query_params.get('id')
            print(course_id)
            if course_id is not None:
                course = Course.objects.get(id=course_id)
                serializer = CourseSerializer(course)
                modules = Module.objects.filter(course=course)
                assignments = Assignment.objects.filter(course=course)
                quizzes = Quiz.objects.filter(course=course)
                teacher_serializer = TeacherSerializer(course.teacher) 
                serialized_data = {
                    **serializer.data,
                    'teacher': teacher_serializer.data,  
                    'num_modules': modules.count(),
                    'num_assignments': assignments.count(),
                    'num_quizzes': quizzes.count(),
                }
                print(serialized_data,88888888888888888888888888888888888888888888)
                return Response(serialized_data,status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND) 

#<-------------------------------------------------------------------------------------------------------------->        
class StudentModule(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        course_id = request.query_params.get('id')
        print(course_id, 888888888888888888888888)

        if course_id is not None:
            try:
                course = Course.objects.get(id=course_id)
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

            except StudentCourse.DoesNotExist:
                return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Course ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
    #<------------------------------------------------------------------------------------------------->
class StudentAssignemntApiView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request):
        try:
            course_id = request.query_params.get('id')
            student_id = request.query_params.get('student_id')
            print(888888888888888888888888888888888888888888888888)
            if course_id is not None and student_id is not None:
                assignments = Assignment.objects.filter(course=course_id)
                assignment_data = []
                for assignment in assignments:
                    print(99999999999999999999999999999999999999999999999999999)
                    serializer = AssignmentSerializer(assignment)
                    student_assignments = StudentAssignment.objects.filter(assignment=assignment, student=student_id).first()
                    print(555555555555555555555555555555555555555555555555555555555555555555)
                    student_assignment_data = StudentAssignmentSerializer(student_assignments).data
                    print(77777777777777777777777777777777777777777777777777777777777777)
                    assignment_data.append({
                        'assignment': serializer.data,
                        'student_assignments': student_assignment_data
                    })
                return Response(assignment_data, status=status.HTTP_200_OK)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request, *args, **kwargs):
        assignment_id = request.data.get('assignment')
        student_id = request.data.get('student')
        existing_submission = StudentAssignment.objects.filter(assignment=assignment_id, student=student_id).first()
        if existing_submission:
            serializer = StudentAssignmentSerializer(existing_submission, data=request.data)
        else:
            serializer = StudentAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
#<--------------------------------------------------------------------------------------------------------------------->
class StudentQuizApiView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request):
        try:
            course_id = request.query_params.get('id')
            student_id = request.query_params.get('student_id')
            print(course_id,77777777777777777777777777777777777)
            if course_id is not None:
                quiz = Quiz.objects.filter(course=course_id)
                student = StudentProfile.objects.get(id=student_id)
                print(quiz)
                
                quiz_data = []
                for quiz_item in quiz:
                    quiz_serializer = QuizSerializer(quiz_item)
                    quiz_questions = Questions.objects.filter(quiz=quiz_item)
                    question_serializer = QuestionSerializer(quiz_questions, many=True)
                    student_quiz = StudentQuiz.objects.filter(student=student_id, quiz=quiz_item).first()
                    
                    # Serialize each instance of StudentQuiz individually
                    student_quiz_serializer = StudentQuizsSerializer(student_quiz)
                    
                    quiz_data.append({
                        'quiz': quiz_serializer.data,
                        'questions': question_serializer.data,
                        'student': student_quiz_serializer.data  # Use .data to get serialized data
                    })
                    
                return Response(quiz_data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        print(request.data,88888888888888888888888888888)
        serializer = StudentQuizsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
#<------------------------------------------------------------------------------------------------------------------->
class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request):
        student_id = request.query_params.get('student_id')
        if student_id is not None:
            try:
                student = StudentProfile.objects.get(id=student_id)
                serializer = StudentSerializer(student)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except StudentProfile.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request):
        student_id = request.data.get('student_id')
        user_id = request.data.get('user_id')
        print(request.data)
        try:
            user=UserAccount.objects.get(id=user_id)
            teacher = StudentProfile.objects.get(id=student_id)
        except StudentProfile.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user_serializer = UserSerializer(user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
        serializer = StudentProfileSerializer(teacher, data=request.data, partial=True)
        print(8888888888888888888888888888888888888888888888)
        if serializer.is_valid():
            print(888888888888888888888888888888888)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#<-------------------------------------------------------------------------------------------------------------------------------------------------------------->    

class RoomId(APIView):
     permission_classes = [IsAuthenticated]
     def get(self, request):
        try:
            course_id = request.query_params.get('id')
            print(course_id,88888888888888888888888888888888888) 
            if course_id is not None:
                course = Course.objects.get(id=course_id)
                room = Room.objects.get(course=course)  # Use get instead of filter
                print(room, 99999999999999999999999999999)
                serializer = RoomSerializer(room)
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        except Room.DoesNotExist:
            return Response({"error": "Room not found for the given course"}, status=status.HTTP_404_NOT_FOUND)

#<----------------------------------------------------------------------------------------------------------------------------->
class CompletionPercentageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            student_id = request.query_params.get('student_id')
            course_id = request.query_params.get('id')
            print(student_id,course_id)
            completed_chapters_count = StudentChapter.objects.filter(student_id=student_id, chapter__module__course_id=course_id).count()
            print(completed_chapters_count,88888888888888888888888888888)
            completed_assignments_count = StudentAssignment.objects.filter(student_id=student_id, assignment__course_id=course_id).count()
            print(completed_assignments_count,77777777777777777777777777777777)
            completed_quizzes_count = StudentQuiz.objects.filter(student_id=student_id, quiz__course_id=course_id).count()
            print(completed_quizzes_count,6666666666666666666666)
            total_chapters_count = Chapter.objects.filter(module__course_id=course_id).count()
            total_assignments_count = Assignment.objects.filter(course_id=course_id).count()
            total_quizzes_count = Quiz.objects.filter(course_id=course_id).count()
            
            # Calculate the completion percentage for each component
            chapters_percentage = (completed_chapters_count / total_chapters_count) * 100 if total_chapters_count != 0 else 0
            assignments_percentage = (completed_assignments_count / total_assignments_count) * 100 if total_assignments_count != 0 else 0
            quizzes_percentage = (completed_quizzes_count / total_quizzes_count) * 100 if total_quizzes_count != 0 else 0
            
            # Calculate the overall completion percentage
            overall_percentage = (chapters_percentage + assignments_percentage + quizzes_percentage) / 4
            
            return Response( overall_percentage, status=status.HTTP_200_OK)
        
        except:
            return Response({'error': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
#<-------------------------------------------------------------------------------------------------------------------------------------------------------------->
class MessageView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            room_id = request.query_params.get('id')
            print(room_id,777777777777777777777777777777777777777777777777777777)
            messages = Message.objects.filter(room=room_id)
            print(messages,88888888888888888888888888888888888888)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found for the given course"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
class StudentChapterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
      try:
        student_id = request.data.get('id')
        chapter_id = request.data.get('chapter')
        print(student_id,chapter_id)
        if student_id and chapter_id:
            print(88888888888888888888888888888888888888888888888888)
            chapter = StudentChapter.objects.filter(student=student_id, chapter=chapter_id).first()
            print(chapter,777777777777777777777777777777777777777777777777777)
            if not chapter:
                data = {'student': student_id, 'chapter': chapter_id}
                serializer = StudentChapterSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    print(77777777777777777777777777777777777777777777777777777777777777777777)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    print(serializer.error)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
      except:
        return Response({"details":"Internal Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
class StudentCertificateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            student = request.query_params.get('id')
            course = request.query_params.get('course')
            print(student,777777777777777777777777777777777777777777777777777777)
            certificate = StudentCertificate.objects.filter(student=student,course=course).first()
            print(certificate,88888888888888888888888888888888888888)
            if certificate is not None: 
                serializer = StudentCertificateSerializer(certificate)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                 return Response({"message": "No certificate exist."}, status=200)
        except certificate.DoesNotExist:
            return Response({"error": "certificate not found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

    def post(self, request):
        try:
            student_id = request.data.get('student')
            print(request.data,7777777777777777777777777777777777777777777777777777777)
            if student_id:
                serializer = StudentCertificateSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"details": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"details":"Internal Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
