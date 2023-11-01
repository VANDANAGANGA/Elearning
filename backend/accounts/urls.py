from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='user-registration'),
    path('generate-otp/', views.GenerateOTP.as_view(), name='generate_otp'),
    path('verify-otp/', views.VerifyOTP.as_view(), name='verify_otp'),

    path('login/',views.MyTokenObtainPairView.as_view()),
    path('logout/',views.MyTokenLogoutView.as_view()),
  
  
    path('coursecategory/',views.CourseCategoryView.as_view(),name='coursecategory'),
    path('teachermanagement/',views.TeacherListView.as_view(),name='teachermanagement')

   
]
