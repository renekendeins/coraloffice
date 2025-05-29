
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity

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
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'certification_level', 'emergency_contact', 'medical_conditions')
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
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
        fields = ('date', 'time', 'dive_site', 'max_participants', 'description')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CustomerDiveActivityForm(forms.ModelForm):
    class Meta:
        model = CustomerDiveActivity
        fields = ('customer', 'activity')
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'activity': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, diving_center=None, dive_schedule=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['customer'].queryset = Customer.objects.filter(diving_center=diving_center)
            self.fields['activity'].queryset = DiveActivity.objects.filter(diving_center=diving_center)
        print("ñññ",dive_schedule)
        if dive_schedule:
            # Exclude customers already participating in this dive
            already_participating = CustomerDiveActivity.objects.filter(
                dive_schedule=dive_schedule['customer'])
            self.fields['customer'].queryset = self.fields['customer'].queryset.exclude(
                id__in=already_participating
            )
