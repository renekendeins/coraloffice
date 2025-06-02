
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity, 
    DivingSite, InventoryItem, DivingGroup, DivingGroupMember, Staff, 
    Course, Enrollment, CourseSession, MedicalForm
)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'country', 'certification_level', 'created_at')
    list_filter = ('country', 'certification_level', 'language', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('diving_center', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Personal Details', {
            'fields': ('country', 'language', 'birthday', 'certification_level')
        }),
        ('Emergency & Medical', {
            'fields': ('emergency_contact', 'medical_conditions')
        }),
        ('Physical Details', {
            'fields': ('weight', 'height', 'foot_size', 'default_tank_size')
        }),
        ('Documents', {
            'fields': ('profile_picture', 'diving_licence', 'diving_insurance', 'medical_check')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Diving Site Admin
@admin.register(DivingSite)
class DivingSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'difficulty_level', 'depth_min', 'depth_max')
    list_filter = ('difficulty_level', 'diving_center')
    search_fields = ('name', 'location')
    fieldsets = (
        ('Basic Information', {
            'fields': ('diving_center', 'name', 'location')
        }),
        ('Diving Details', {
            'fields': ('depth_min', 'depth_max', 'difficulty_level')
        }),
        ('Additional Information', {
            'fields': ('description', 'special_requirements')
        })
    )

# Dive Activity Admin
@admin.register(DiveActivity)
class DiveActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'diving_center', 'max_participants', 'price', 'duration')
    list_filter = ('diving_center', 'max_participants')
    search_fields = ('name', 'description')

# Dive Schedule Admin
@admin.register(DiveSchedule)
class DiveScheduleAdmin(admin.ModelAdmin):
    list_display = ('dive_site', 'date', 'time', 'max_participants', 'current_participants_count')
    list_filter = ('date', 'dive_site', 'diving_center')
    search_fields = ('dive_site__name', 'special_notes')
    readonly_fields = ('current_participants_count',)
    
    def current_participants_count(self, obj):
        return obj.customer_activities.count()
    current_participants_count.short_description = 'Current Participants'

# Customer Dive Activity Admin
@admin.register(CustomerDiveActivity)
class CustomerDiveActivityAdmin(admin.ModelAdmin):
    list_display = ('customer', 'dive_schedule', 'activity', 'status', 'is_paid', 'tank_size')
    list_filter = ('status', 'is_paid', 'tank_size', 'activity', 'dive_schedule__date')
    search_fields = ('customer__first_name', 'customer__last_name', 'dive_schedule__dive_site__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'dive_schedule', 'activity', 'assigned_staff', 'course_session')
        }),
        ('Equipment & Services', {
            'fields': ('tank_size', 'needs_wetsuit', 'needs_bcd', 'needs_regulator', 'needs_guide', 'needs_insurance')
        }),
        ('Status & Payment', {
            'fields': ('status', 'has_arrived', 'is_paid')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Staff Admin
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'certification_level', 'hire_date', 'is_active')
    list_filter = ('certification_level', 'is_active', 'hire_date')
    search_fields = ('first_name', 'last_name', 'email', 'certification_number')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('diving_center', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Professional Details', {
            'fields': ('certification_level', 'certification_number', 'languages', 'experience_years')
        }),
        ('Employment', {
            'fields': ('hire_date', 'hourly_rate', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('specialties', 'bio', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_type', 'total_dives', 'duration_days', 'price', 'is_active')
    list_filter = ('course_type', 'is_active', 'diving_center')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('diving_center', 'name', 'course_type')
        }),
        ('Course Details', {
            'fields': ('description', 'total_dives', 'duration_days', 'price')
        }),
        ('Requirements', {
            'fields': ('prerequisites', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Enrollment Admin
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'course', 'enrollment_date', 'status', 'primary_instructor')
    list_filter = ('status', 'enrollment_date', 'course', 'primary_instructor')
    search_fields = ('customer__first_name', 'customer__last_name', 'course__name')
    readonly_fields = ('enrollment_date',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'course', 'primary_instructor')
        }),
        ('Progress', {
            'fields': ('status', 'completion_date', 'certification_number')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('enrollment_date',)
        })
    )

# Course Session Admin
@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'session_number', 'title', 'scheduled_date', 'is_completed')
    list_filter = ('is_completed', 'session_type', 'scheduled_date')
    search_fields = ('enrollment__customer__first_name', 'enrollment__customer__last_name', 'title')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('enrollment', 'session_number', 'title', 'session_type')
        }),
        ('Scheduling', {
            'fields': ('dive_slot', 'scheduled_date', 'assigned_instructor')
        }),
        ('Progress', {
            'fields': ('is_completed', 'completion_date', 'instructor_notes')
        }),
        ('Content', {
            'fields': ('description', 'objectives', 'requirements')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Inventory Item Admin
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'size', 'quantity_available', 'quantity_total', 'condition')
    list_filter = ('category', 'size', 'condition', 'diving_center')
    search_fields = ('name', 'notes')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('diving_center', 'name', 'category', 'size')
        }),
        ('Inventory', {
            'fields': ('quantity_total', 'quantity_available', 'condition')
        }),
        ('Maintenance', {
            'fields': ('purchase_date', 'last_maintenance')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Diving Group Admin
@admin.register(DivingGroup)
class DivingGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'contact_person', 'arrival_date', 'departure_date')
    list_filter = ('country', 'arrival_date', 'departure_date')
    search_fields = ('name', 'contact_person', 'email')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('diving_center', 'name', 'country')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'email', 'phone')
        }),
        ('Visit Details', {
            'fields': ('arrival_date', 'departure_date', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Diving Group Member Admin
@admin.register(DivingGroupMember)
class DivingGroupMemberAdmin(admin.ModelAdmin):
    list_display = ('customer', 'group', 'role', 'joined_date')
    list_filter = ('role', 'joined_date', 'group')
    search_fields = ('customer__first_name', 'customer__last_name', 'group__name')
    readonly_fields = ('joined_date',)

# Medical Form Admin
@admin.register(MedicalForm)
class MedicalFormAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'submitted_at')
    list_filter = ('submitted_at', 'medical_conditions')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('submitted_at',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'emergency_contact')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions',)
        }),
        ('Metadata', {
            'fields': ('submitted_at',)
        })
    )

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register UserProfile separately if needed
admin.site.register(UserProfile)
