from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='user-registration'),
    path('generate-otp/', views.GenerateOTP.as_view(), name='generate_otp'),
    path('verify-otp/', views.VerifyOTP.as_view(), name='verify_otp'),

    path('login/',views.MyTokenObtainPairView.as_view()),
    path('logout/',views.MyTokenLogoutView.as_view()),
    path('courses/',views.CourseView.as_view(),name='courses'),
    path('coursedetailsmain/',views.CourseDetailsAPIView.as_view()),
    path('team/',views.TeamListView.as_view(),name='teamlistview'),
    path('about/',views.AboutView.as_view(),name='aboutview'),
    path('contact/',views.ContactFormView.as_view(),name='contactformview'),
    path('profilepic/',views.ProfilePic.as_view(),name='profilepic'),
    
  
  
    path('coursecategory/',views.CourseCategoryView.as_view(),name='coursecategory'),
    path('teachermanagement/',views.TeacherListView.as_view(),name='teachermanagement'),
    path('studentmanagement/',views.StudentListView.as_view(),name='studentmanagement'),
    path('admincourse/',views.AdminCourse.as_view(),name='admincourse'),
    path('dashboard/',views.DashBoard.as_view(),name='dashboard'),
     path('salesreport/',views.SalesReport.as_view(),name='salesreport'),



  
     path('roomid/',views.RoomId.as_view(),name='roomid'),
     path('messages/',views.MessageView.as_view(),name='message'),



    path('teachercourses/',views.TeacherCourse.as_view(),name='teachercourses'),
    path('coursedetails/',views.CourseDetailView.as_view(),name='coursedetails'),
    path('module/',views.ModuleView.as_view(),name='module'),
    path('chapter/',views.ChapterView.as_view(),name='chapter'),
    path('teacherassignment/', views.TeacherAssignemnt.as_view(), name='teacherassignment'),
    path('teacherquiz/', views.TeacherQuiz.as_view(), name='teacherquiz'),
    path('teacherquestions/', views.TeacherQuestions.as_view(), name='teacherquestions'),
    path('teacherallassignment/', views.TeacherAllAssignment.as_view(), name='teacherallassignment'),
     path('teacherallquiz/', views.TeacherAllQuiz.as_view(), name='teacherallquiz'),
    path('shedule/',views.SheduleApiView.as_view(),name='sheduleview'),
    path('teacherprofile/',views.TeacherProfileView.as_view(),name='teacherprofile'),

    path('create-razorpay-order/',views.OrderApiView.as_view(),name='orderview'),
    path('handle-payment-success/',views.HandlePaymentSuccessView.as_view(),name='handlepayment'),

    path('check-payment/',views.CheckPayment.as_view(),name='check_payment'),
    path('studentcourse/',views.StudentCourseApiView.as_view(),name='studentcourse'),
    path('studentcoursedetails/',views.StudentCourseDetails.as_view(),name='studentcoursedetails'),
    path('studentmodule/',views.StudentModule.as_view(),name='studentmodule'),
    path('studentassignment/',views.StudentAssignemntApiView.as_view(),name='studentassignment'),
    path('studentquiz/',views.StudentQuizApiView.as_view(),name='studentquiz'),
    path('studentprofile/',views.StudentProfileView.as_view(),name='studentprofile'),
    path('studentchapter/',views.StudentChapterView.as_view(),name='studentchapter'),
    path('coursecompletion/',views.CompletionPercentageAPIView.as_view(),name='coursecompletion'),
     path('coursecertificate/',views.StudentCertificateView.as_view(),name='studentcertificate'),




 

 





   
]
