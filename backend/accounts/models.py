from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

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
     
    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.role = 1
        user.save(using=self._db)
        return user
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
    profile_pic = models.ImageField(upload_to='user/', null=True, blank=True, default='user/user.png')
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

# class TeacherProfile(models.Model):
#     user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='teacher_profile')
#     experience = models.CharField(max_length=100, blank=True)
#     qualification = models.CharField(max_length=100, blank=True)
#     about = models.TextField(blank=True)

#     def __str__(self):
#         return self.user.email

class CourseCategory(models.Model):
    title=models.CharField(max_length=100,unique=True)
    icon_url=models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return self.title
