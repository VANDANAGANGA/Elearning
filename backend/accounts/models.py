from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models import Manager



# Create your models here.
def upload_to(instance, filename):
    return f'profile_pics/{filename}'

class UserAccountManager(BaseUserManager):
    def create_user(self, email, full_name, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not full_name:
            raise ValueError("The Full Name field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
     
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 1)  # Assuming superusers have the role of 'Admin'

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password=password, **extra_fields)
class UserAccount(AbstractBaseUser, PermissionsMixin):
    ADMIN = 1
    STUDENT = 2
    TEACHER = 3

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher')
    )

    email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(null=True, blank=True)
    full_name = models.CharField(max_length=200)
    profile_pic = models.ImageField(upload_to=upload_to, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=2)
    is_admin=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Add is_staff field
    is_superuser = models.BooleanField(default=False) 
   
    

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_accounts'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_accounts'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name','phone_number']

    objects = UserAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
    

class TeacherProfile(models.Model):
    user = models.OneToOneField('UserAccount', on_delete=models.CASCADE, related_name='teacher_profile')
    years_of_experience = models.PositiveIntegerField()
    job_role=models.CharField()
    company_name = models.CharField(max_length=255)
    about = models.CharField(max_length=500)
    account = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    def __str__(self):
           return f"{str(self.user.full_name)}'s Teacher Profile"

class StudentProfile(models.Model):
    user=models.OneToOneField('UserAccount',on_delete=models.CASCADE,related_name='student_profile')  
    highest_education=models.CharField(max_length=100)
    specialization=models.CharField(max_length=200,null=True)
    mother_name=models.CharField(null=True)
    father_name=models.CharField(null=True)
    house_name=models.CharField()
    street=models.CharField()
    city=models.CharField()
    state=models.CharField()
    country=models.CharField()
    pin=models.CharField()

    def __str__(self):
        return f"{self.user.full_name}'s Student Profile",self.id
    

class CourseCategory(models.Model):
    title=models.CharField(max_length=100,unique=True)
    icon_url=models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return self.title

class Course(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    created_at = models.DateField(auto_now=True)
    about=models.TextField(max_length=1000)

         
    
class Module(models.Model):
    module_no= models.IntegerField()
    course =models.ForeignKey(Course,on_delete=models.CASCADE)
    module_title=models.CharField()    

    def __str__(self):
        return self.module_title
    

class Chapter(models.Model):
    chapter_no=models.IntegerField()
    module=models.ForeignKey(Module,on_delete=models.CASCADE)
    chapter_title=models.CharField()
    video=models.FileField(upload_to='videos/')
    
    def __str__(self):
       return self.chapter_title
        
class Assignment(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)  
    assignment_no=models.IntegerField()
    assignment_title=models.CharField()
    pdf=models.FileField(upload_to='assignments/')
    
    
   
class Quiz(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)  
    quiz_no=models.IntegerField()
    quiz_title=models.CharField()

    
class Questions(models.Model):
    ANSWER_CHOICES = [
        ('A', 'option_a'),
        ('B', 'option_b'),
        ('C', 'option_c'),
        ('D', 'option_d'),
    ]

    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE)
    question_no=models.IntegerField()
    question=models.CharField()
    option_a=models.CharField()
    option_b=models.CharField()
    option_c=models.CharField()
    option_d=models.CharField()
    answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)

    def __str__(self):
        return f"Question {self.question_no} - {self.question} ({self.quiz})"

class Masterclass(models.Model):    
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    start_date = models.DateField()
    time=models.TimeField()
    about=models.TextField(max_length=1000)


    def update_is_active_status(self):
        current_datetime = timezone.now()
        if current_datetime > timezone.datetime.combine(self.start_date, self.time):
            self.is_active = False
            self.save()   



class Shedule(models.Model):    
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    date = models.DateField()
    about = models.TextField(max_length=1000)
    completed = models.BooleanField(default=False)
    

class Order(models.Model):
    student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_payment_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)
    months = models.IntegerField(default=0)

  
    def isValid(self):
        now = timezone.now()
        active_duration = now - self.order_date
        months_active = active_duration.days // 30  # Assuming a month has 30 days

        if months_active >= self.months:
            self.isPaid = True
        else:
            self.isPaid = False

        self.save()
        return self.isPaid
    
class StudentCourse(models.Model):
    student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - Amount: {self.student}, Student: {self.course},"
    
    
class StudentChapter(models.Model):
    student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    chapter=models.ForeignKey(Chapter,on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=True)    
    

class StudentAssignment(models.Model):
    student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    assignment=models.ForeignKey(Assignment,on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now=True)
    answer=models.FileField(upload_to='studentassignments/')
    verified=models.BooleanField(default=False)

class StudentQuiz(models.Model):
    student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now=True)
    mark=models.IntegerField()
    response=models.FileField(upload_to='studentquiz/')

class StudentCertificate(models.Model):
    student=models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    teacher=models.CharField()
    course=models.CharField()
    date=models.DateField(auto_now=True)

class Room(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="taught_classes")
    students = models.ManyToManyField(StudentProfile, related_name="enrolled_classes", blank=True)

    def __str__(self):
        return f"Room({self.id})"
    
class Message(models.Model):
    room = models.ForeignKey("accounts.Room", on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message({self.user} {self.room})"    
    

    