
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity, DivingSite, InventoryItem, DivingGroup

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
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'country', 'language', 'birthday', 'certification_level', 'emergency_contact', 'medical_conditions', 'weight', 'height', 'foot_size')
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'kg'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'cm'}),
            'foot_size': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'EU size'}),
        }

class DiveActivityForm(forms.ModelForm):
    class Meta:
        model = DiveActivity
        fields = ('name', 'description', 'duration_minutes', 'price')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DiveScheduleForm(forms.ModelForm):
    class Meta:
        model = DiveSchedule
        fields = ('date', 'time', 'dive_site', 'max_participants', 'description', 'special_notes')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'special_notes': forms.Textarea(attrs={'rows': 2}),
        }

class CustomerDiveActivityForm(forms.ModelForm):
    customer_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Start typing customer name...',
            'autocomplete': 'off',
            'id': 'customer-search'
        }),
        label='Search Customer'
    )
    
    class Meta:
        model = CustomerDiveActivity
        fields = ('customer', 'activity', 'tank_size', 'needs_wetsuit', 'needs_bcd', 'needs_regulator', 'needs_guide', 'needs_insurance', 'status', 'has_arrived', 'is_paid')
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control', 'style': 'display: none;'}),
            'activity': forms.Select(attrs={'class': 'form-control'}),
            'tank_size': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, diving_center=None, dive_schedule=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['customer'].queryset = Customer.objects.filter(diving_center=diving_center)
            self.fields['activity'].queryset = DiveActivity.objects.filter(diving_center=diving_center)
        
        if dive_schedule:
            # Exclude customers already participating in this dive
            already_participating = CustomerDiveActivity.objects.filter(
                dive_schedule=dive_schedule).values_list('customer_id', flat=True)
            self.fields['customer'].queryset = self.fields['customer'].queryset.exclude(
                id__in=already_participating)

class QuickUpdateParticipantForm(forms.ModelForm):
    class Meta:
        model = CustomerDiveActivity
        fields = ('tank_size', 'needs_wetsuit', 'needs_bcd', 'needs_regulator', 'needs_guide', 'needs_insurance', 'status', 'has_arrived', 'is_paid')
        widgets = {
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

class MedicalForm(forms.ModelForm):
    """Form for external users to fill medical information"""
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'country', 'language', 'birthday', 'certification_level', 'emergency_contact', 'medical_conditions', 'weight', 'height', 'foot_size')
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please list any medical conditions, allergies, medications, or health concerns...'}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'kg'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'cm'}),
            'foot_size': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'EU size'}),
        }
