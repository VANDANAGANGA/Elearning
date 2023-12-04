from django.contrib import admin
from.models import UserAccount,CourseCategory,Course,TeacherProfile,StudentProfile,Module,Chapter
from django.contrib.auth.admin import UserAdmin
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'phone_number', 'is_active', 'role', 'is_superuser')
    search_fields = ('email', 'phone_number')
    
    # Specify a valid field for ordering, for example, 'id'
    ordering = ('id',)
    actions = ['delete_selected']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name' ,'role', 'phone_number', 'display_pic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Qualifications',{'fields': ('city','state','country','qualification','skills','subjects','category')})
        # ('Important dates', {'fields': ('last_login',)}),
    )

admin.site.register(UserAccount, CustomUserAdmin)
admin.site.register(CourseCategory)
admin.site.register(Course)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)
admin.site.register(Module)
admin.site.register(Chapter)