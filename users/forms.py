from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity, DivingSite, InventoryItem, DivingGroup, Staff, Course, CourseEnrollment, CourseSession

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    is_diving_center = forms.BooleanField(required=False, help_text='Check if you are registering a diving center.')
    business_name = forms.CharField(max_length=100, required=False, help_text='Required if you are a diving center.')
    business_license = forms.CharField(max_length=50, required=False, help_text='Your business license number.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'location', 'birth_date', 'avatar', 'phone_number')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'country', 'language', 'birthday', 'certification_level', 'emergency_contact', 'medical_conditions', 'weight', 'height', 'foot_size', 'default_tank_size', 'profile_picture', 'diving_licence', 'diving_insurance', 'medical_check')
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'kg'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'cm'}),
            'foot_size': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'EU size'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
            'diving_licence': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
            'diving_insurance': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
            'medical_check': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
        }

class DiveActivityForm(forms.ModelForm):
    class Meta:
        model = DiveActivity
        fields = ('name', 'description', 'duration_minutes', 'price')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DiveScheduleForm(forms.ModelForm):
    dive_site = forms.ModelChoiceField(
        queryset=DivingSite.objects.none(),
        empty_label="Select a diving site",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Choose a dive site for this dive"
    )

    class Meta:
        model = DiveSchedule
        fields = ('date', 'time', 'dive_site', 'max_participants', 'description', 'special_notes')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'special_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, diving_center=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['dive_site'].queryset = DivingSite.objects.filter(diving_center=diving_center).order_by('name')

class CustomerDiveActivityForm(forms.ModelForm):
    customer_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Start typing customer or group name...',
            'autocomplete': 'off',
            'id': 'customer-search'
        }),
        label='Search Customer or Group'
    )

    selected_group = forms.ModelChoiceField(
        queryset=DivingGroup.objects.none(),
        required=False,
        widget=forms.HiddenInput(),
        label='Selected Group'
    )

    class Meta:
        model = CustomerDiveActivity
        fields = ('customer', 'course', 'assigned_staff', 'tank_size', 'needs_wetsuit', 'needs_bcd', 'needs_regulator', 'needs_guide', 'needs_insurance')
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control', 'style': 'display: none;', 'data-default-tank': 'true'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'assigned_staff': forms.Select(attrs={'class': 'form-control'}),
            'tank_size': forms.Select(attrs={'class': 'form-control', 'id': 'tank-size-select'}),
        }

    def __init__(self, diving_center=None, dive_schedule=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['customer'].queryset = Customer.objects.filter(diving_center=diving_center)
            # Filter courses to show both regular courses and those marked as "just one dive"
            # Order with "just one dive" courses first
            self.fields['course'].queryset = Course.objects.filter(diving_center=diving_center, is_active=True).order_by('-just_one_dive', 'name')
            self.fields['selected_group'].queryset = DivingGroup.objects.filter(diving_center=diving_center)
            self.fields['assigned_staff'].queryset = Staff.objects.filter(diving_center=diving_center, status='ACTIVE')
            self.fields['assigned_staff'].empty_label = "Select instructor (optional)"

        if dive_schedule:
            # Exclude customers already participating in this dive
            already_participating = CustomerDiveActivity.objects.filter(
                dive_schedule=dive_schedule).values_list('customer_id', flat=True)
            self.fields['customer'].queryset = self.fields['customer'].queryset.exclude(
                id__in=already_participating)

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Automatically set equipment needs if course includes material
        if instance.course and instance.course.includes_material:
            instance.needs_wetsuit = True
            instance.needs_bcd = True
            instance.needs_regulator = True
        
        if commit:
            instance.save()
        return instance

class QuickUpdateParticipantForm(forms.ModelForm):
    class Meta:
        model = CustomerDiveActivity
        fields = ('course', 'tank_size', 'needs_wetsuit', 'needs_bcd', 'needs_regulator', 'needs_guide', 'needs_insurance', 'status', 'has_arrived', 'is_paid')
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'tank_size': forms.Select(attrs={'class': 'form-control'}),
        }

class DivingSiteForm(forms.ModelForm):
    class Meta:
        model = DivingSite
        fields = ('name', 'location', 'depth_min', 'depth_max', 'difficulty_level', 'description', 'special_requirements')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'special_requirements': forms.Textarea(attrs={'rows': 2}),
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ('name', 'category', 'size', 'quantity_total', 'quantity_available', 'condition', 'purchase_date', 'last_maintenance', 'notes')
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DivingGroupForm(forms.ModelForm):
    class Meta:
        model = DivingGroup
        fields = ('name', 'country', 'contact_person', 'email', 'phone', 'description', 'arrival_date', 'departure_date')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
        }

class QuickCustomerForm(forms.ModelForm):
    """Simplified form for quickly adding customers in group management"""
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'country', 'certification_level', 'default_tank_size')
        widgets = {
            'country': forms.Select(attrs={'class': 'form-control'}),
            'certification_level': forms.Select(attrs={'class': 'form-control'}),
            'default_tank_size': forms.Select(attrs={'class': 'form-control'}),
        }

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'certification_level', 'certification_number', 'languages', 'experience_years', 'specialties', 'hire_date', 'status', 'hourly_rate', 'profile_picture', 'notes')
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'specialties': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'languages': forms.TextInput(attrs={'placeholder': 'e.g., English, Spanish, French'}),
            'hourly_rate': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class MedicalForm(forms.ModelForm):
    """Form for external users to fill medical information"""
    # Medical questions as boolean fields
    heart_problems = forms.BooleanField(required=False, label="Do you have heart problems?")
    high_blood_pressure = forms.BooleanField(required=False, label="Do you have high blood pressure?")
    breathing_problems = forms.BooleanField(required=False, label="Do you have breathing problems or asthma?")
    diabetes = forms.BooleanField(required=False, label="Do you have diabetes?")
    epilepsy = forms.BooleanField(required=False, label="Do you have epilepsy or seizures?")
    pregnant = forms.BooleanField(required=False, label="Are you pregnant?")
    medications = forms.BooleanField(required=False, label="Are you taking any medications?")
    allergies = forms.BooleanField(required=False, label="Do you have any allergies?")
    surgery_recent = forms.BooleanField(required=False, label="Have you had surgery in the last 6 months?")
    ear_problems = forms.BooleanField(required=False, label="Do you have ear or sinus problems?")
    swimming_ability = forms.ChoiceField(
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        label="Swimming ability",
        required=True
    )

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'country', 'language', 'birthday', 'certification_level', 'emergency_contact', 'medical_conditions', 'weight', 'height', 'foot_size', 'default_tank_size')
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please provide additional medical information or details about any conditions mentioned above...'}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'kg'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'cm'}),
            'foot_size': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'EU size'}),
            'language': forms.Select(choices=[
                ('EN', 'English'),
                ('ES', 'Español'),
                ('FR', 'Français'),
                ('DE', 'Deutsch'),
                ('NL', 'Nederlands'),
            ])
        }




class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'course_type', 'description', 'total_dives', 'duration_days', 'price', 'prerequisites', 'is_active', 'just_one_dive', 'includes_material', 'includes_instructor', 'includes_insurance']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'prerequisites': forms.Textarea(attrs={'rows': 2}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class CourseEnrollmentForm(forms.ModelForm):
    class Meta:
        model = CourseEnrollment
        fields = ['customer', 'course', 'primary_instructor', 'start_date', 'notes', 'price_paid', 'is_paid']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'price_paid': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, diving_center=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['customer'].queryset = Customer.objects.filter(diving_center=diving_center)
            self.fields['course'].queryset = Course.objects.filter(diving_center=diving_center, is_active=True)
            self.fields['primary_instructor'].queryset = Staff.objects.filter(diving_center=diving_center, status='ACTIVE')
            self.fields['primary_instructor'].empty_label = "Select instructor (optional)"

class CourseSessionForm(forms.ModelForm):
    class Meta:
        model = CourseSession
        fields = ['session_number', 'session_type', 'title', 'description', 'skills_covered', 'instructor', 'scheduled_date', 'scheduled_time']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'skills_covered': forms.Textarea(attrs={'rows': 2}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, diving_center=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['instructor'].queryset = Staff.objects.filter(diving_center=diving_center, status='ACTIVE')
            self.fields['instructor'].empty_label = "Select instructor (optional)"

class CourseSessionScheduleForm(forms.Form):
    def __init__(self, diving_center, session, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get available dive schedules for this diving center
        from datetime import date
        available_dives = DiveSchedule.objects.filter(
            diving_center=diving_center,
            date__gte=date.today()
        ).order_by('date', 'time')

        self.fields['dive_schedule'] = forms.ModelChoiceField(
            queryset=available_dives,
            empty_label="Select a dive slot",
            widget=forms.Select(attrs={'class': 'form-control'}),
            help_text="Choose an available dive slot for this lesson"
        )

        # Add primary instructor field
        instructors = Staff.objects.filter(
            diving_center=diving_center,
            status='ACTIVE'
        )

        self.fields['instructor'] = forms.ModelChoiceField(
            queryset=instructors,
            required=False,
            empty_label="Select primary instructor",
            widget=forms.Select(attrs={'class': 'form-control'}),
            initial=session.enrollment.primary_instructor,
            help_text="Primary instructor responsible for this lesson"
        )

        # Add assistant instructors field
        self.fields['assistant_instructors'] = forms.ModelMultipleChoiceField(
            queryset=instructors,
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            help_text="Additional staff members to assist with this lesson"
        )

        # Add session notes field
        self.fields['instructor_notes'] = forms.CharField(
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            required=False,
            help_text="Notes about this lesson or special requirements"
        )


class LessonCompletionForm(forms.Form):
    GRADE_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('SATISFACTORY', 'Satisfactory'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
    ]

    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    instructor_notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False,
        help_text="Instructor's observations and feedback"
    )

    student_feedback = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Student's feedback about the lesson"
    )

    completion_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=False,
        help_text="Leave blank to use current date/time"
    )