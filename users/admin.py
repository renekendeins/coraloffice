
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from .models import (
    UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity, 
    DivingSite, InventoryItem, DivingGroup, DivingGroupMember, Staff, 
    Course, CourseSession, CourseEnrollment, 
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
    list_display = ('first_name', 'last_name', 'email', 'country', 'certification_level', 'has_medical_form', 'created_at')
    list_filter = ('country', 'certification_level', 'language', 'created_at', 'swimming_ability')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'medical_questionnaire_display')
    fieldsets = (
        ('Basic Information', {
            'fields': ('diving_center', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Personal Details', {
            'fields': ('country', 'language', 'birthday', 'certification_level')
        }),
        ('Emergency & Medical', {
            'fields': ('emergency_contact', 'medical_conditions', 'swimming_ability')
        }),
        ('Medical Questionnaire', {
            'fields': ('medical_questionnaire_display',),
            'classes': ('collapse',)
        }),
        ('Physical Details', {
            'fields': ('weight', 'height', 'foot_size', 'default_tank_size')
        }),
        ('Documents', {
            'fields': ('profile_picture', 'diving_licence', 'diving_insurance', 'medical_check', 'signature')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )
    
    def has_medical_form(self, obj):
        return bool(obj.medical_questionnaire_answers)
    has_medical_form.boolean = True
    has_medical_form.short_description = 'Has Medical Form'
    
    def medical_questionnaire_display(self, obj):
        if not obj.medical_questionnaire_answers:
            return "No medical questionnaire submitted"
        
        html = "<div style='max-width: 800px;'>"
        html += "<h3>Medical Questionnaire Answers</h3>"
        
        questions = {
            'pregunta_1': 'I have had problems with my lungs/breathing, heart or blood',
            'pregunta_1_1': 'Chest surgery, heart surgery, heart valve surgery, implantable cardiovascular device (e.g. stent, pacemaker, replaceable valve), pneumothorax, and/or collapsed lung.',
            'pregunta_1_2': 'Asthma, wheezing, severe allergies, hay fever or congested airways within the last 12 months that limits my physical activity/exercise.',
            'pregunta_1_3': 'A problem with lung function or chest disease.',
            'pregunta_1_4': 'High blood pressure, or take medication to control blood pressure.',
            'pregunta_2': 'I have had problems with my brain or nervous system',
            'pregunta_2_1': 'Behavioral health, mental or psychological problems that require medication or hospitalization.',
            'pregunta_2_2': 'Head injury with or without loss of consciousness within the last 12 months.',
            'pregunta_2_3': 'Persistent problem with balance, dizziness, fainting, seizures, convulsions or epilepsy.',
            'pregunta_2_4': 'Inability to perform moderately strenuous exercise (e.g. walk 1.6 km/1 mile within 12 minutes).',
            'pregunta_3': 'I have had problems with my stomach, intestines, or bowels',
            'pregunta_4': 'I have had problems with my muscles, bones or joints',
            'pregunta_4_1': 'Muscle, bone or joint injury.',
            'pregunta_4_2': 'Chronic low back problems.',
            'pregunta_4_3': 'Limitation of normal physical activity.',
            'pregunta_4_4': 'Limitation of movement.',
            'pregunta_5': 'I have diabetes',
            'pregunta_6': 'I have had problems with my kidneys, bladder or intestines',
            'pregunta_6_1': 'Medical or surgical treatment of the digestive system within the last 12 months.',
            'pregunta_6_2': 'History of problems with decompression sickness and/or barotrauma.',
            'pregunta_6_3': 'Hernia.',
            'pregunta_6_4': 'Active ulcer or ulcer surgery within the last 12 months.',
            'pregunta_6_5': 'Frequent diarrhea or blood in urine.',
            'pregunta_7': 'I have had other important medical problems',
            'pregunta_7_1': 'Pregnant, or trying to become pregnant.',
            'pregunta_7_2': 'Over 45 years of age.',
            'pregunta_7_3': 'Difficulty equalizing ears or sinus pain.',
            'pregunta_7_4': 'Sinus surgery within the last 12 months.',
            'pregunta_8': 'I take medications on a regular basis (except birth control or malaria prevention)',
            'pregunta_8_1': 'Prescription or over-the-counter medications within the last 12 months (except birth control or malaria prevention).',
            'pregunta_8_2': 'Previous adverse reaction to any medication.',
            'pregunta_8_3': 'Currently under the care of a physician.',
            'pregunta_8_4': 'Have been advised against participating in sports or exercise.',
            'pregunta_8_5': 'Been a patient in a hospital, surgical or emergency facility within the last 12 months.',
            'pregunta_9': 'I have had problems with recreational drugs',
            'pregunta_9_1': 'Used tobacco products within the last 12 months.',
            'pregunta_9_2': 'Used alcohol, prescription or over-the-counter drugs within the last 12 months.',
            'pregunta_9_3': 'Been told I have a drinking problem.',
            'pregunta_9_4': 'Failed a drug or alcohol test required by an employer.',
            'pregunta_9_5': 'Been arrested for driving while under the influence of alcohol or drugs.',
            'pregunta_9_6': 'Been in treatment for alcohol or drug use.',
            'pregunta_10': 'I have used marijuana/cannabis in any form within the last 12 months'
        }
        
        for key, question in questions.items():
            answer = obj.medical_questionnaire_answers.get(key, False)
            status = "YES" if answer else "NO"
            color = "red" if answer else "green"
            html += f"<div style='margin-bottom: 10px; padding: 10px; border-left: 3px solid {color};'>"
            html += f"<strong>{question}</strong><br>"
            html += f"<span style='color: {color}; font-weight: bold;'>{status}</span>"
            html += "</div>"
        
        html += "</div>"
        return mark_safe(html)
    medical_questionnaire_display.short_description = 'Medical Questionnaire'

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
    list_display = ('name', 'diving_center', 'price')
    list_filter = ('diving_center',)
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
    list_display = ('customer', 'course', 'dive_schedule', 'status', 'tank_size', 'assigned_staff')
    list_filter = ('status', 'course', 'dive_schedule__date', 'tank_size')
    search_fields = ('customer__first_name', 'customer__last_name', 'course__name')
    raw_id_fields = ('customer', 'dive_schedule', 'course', 'assigned_staff', 'course_session')

# Keep the old registration for backwards compatibility
# @admin.register(CustomerDiveActivity)
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
    list_display = ('first_name', 'last_name', 'certification_level', 'hire_date')
    list_filter = ('certification_level', 'hire_date')
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
            'fields': ('hire_date', 'hourly_rate')
        }),
        ('Additional Information', {
            'fields': ('specialties', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_type', 'total_dives', 'duration_days', 'price', 'is_active', 'just_one_dive')
    list_filter = ('course_type', 'is_active', 'just_one_dive', 'diving_center')
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
            'fields': ('prerequisites', 'is_active', 'just_one_dive')
        }),
        ('Inclusions', {
            'fields': ('includes_material', 'includes_instructor', 'includes_insurance')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )

# Enrollment Admin
@admin.register(CourseEnrollment)
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
            'fields': ('status', 'completion_date')
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
    list_display = ('enrollment', 'session_number', 'title', 'scheduled_date', 'status')
    # list_filter = ('status', 'session_type', 'scheduled_date')
    # search_fields = ('enrollment__customer__first_name', 'enrollment__customer__last_name', 'title')
    # readonly_fields = ('created_at',)
    # fieldsets = (
    #     ('Basic Information', {
    #         'fields': ('enrollment', 'session_number', 'title', 'session_type')
    #     }),
    #     ('Scheduling', {
    #         'fields': ('dive_slot', 'scheduled_date', 'assigned_instructor')
    #     }),
    #     ('Progress', {
    #         'fields': ('is_completed', 'completion_date', 'instructor_notes')
    #     }),
    #     ('Content', {
    #         'fields': ('description', 'objectives', 'requirements')
    #     }),
    #     ('Metadata', {
    #         'fields': ('created_at',)
    #     })
    # )

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
    list_display = ('customer', 'group')
    list_filter = ('group',)
    search_fields = ('customer__first_name', 'customer__last_name', 'group__name')

# Medical Form Admin
# @admin.register(MedicalForm)
# class MedicalFormAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'email', 'phone_number', 'submitted_at')
#     list_filter = ('submitted_at', 'medical_conditions')
#     search_fields = ('first_name', 'last_name', 'email', 'phone_number')
#     readonly_fields = ('submitted_at',)
#     fieldsets = (
#         ('Personal Information', {
#             'fields': ('first_name', 'last_name', 'email', 'phone_number', 'emergency_contact')
#         }),
#         ('Medical Information', {
#             'fields': ('medical_conditions',)
#         }),
#         ('Metadata', {
#             'fields': ('submitted_at',)
#         })
#     )

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register UserProfile separately if needed
admin.site.register(UserProfile)
