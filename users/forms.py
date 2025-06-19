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
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        required=True
    )

    class Meta:
        model = Customer
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'country',
            'language',
            'birthday',
            'certification_level',
            'emergency_contact',
            'medical_conditions',
            'weight',
            'height',
            'foot_size',
            'default_tank_size',
            'profile_picture',
            'diving_licence',
            'diving_insurance',
            'medical_check',
        )
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'phone_number': 'Número de teléfono',
            'country': 'País',
            'language': 'Idioma',
            'birthday': 'Fecha de nacimiento',
            'certification_level': 'Nivel de certificación',
            'emergency_contact': 'Contacto de emergencia',
            'medical_conditions': 'Condiciones médicas',
            'weight': 'Peso (kg)',
            'height': 'Altura (cm)',
            'foot_size': 'Talla de pie (EU)',
            'default_tank_size': 'Tamaño de botella por defecto',
            'profile_picture': 'Foto de perfil',
            'diving_licence': 'Licencia de buceo',
            'diving_insurance': 'Seguro de buceo',
            'medical_check': 'Revisión médica',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'certification_level': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'kg', 'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'cm', 'class': 'form-control'}),
            'foot_size': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'EU size', 'class': 'form-control'}),
            'default_tank_size': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'diving_licence': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png', 'class': 'form-control'}),
            'diving_insurance': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png', 'class': 'form-control'}),
            'medical_check': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        birthday = self.initial.get('birthday') or self.instance.birthday
        if birthday:
            self.initial['birthday'] = birthday.strftime('%Y-%m-%d')



class DiveActivityForm(forms.ModelForm):
    class Meta:
        model = DiveActivity
        fields = ('name', 'description', 'duration_minutes', 'price')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DiveScheduleForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        required=True
    )
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
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'special_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, diving_center=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['dive_site'].queryset = DivingSite.objects.filter(diving_center=diving_center).order_by('name')
        
        date = self.initial.get('date') or self.instance.date
        if date:
            self.initial['date'] = date.strftime('%Y-%m-%d')

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
            self.fields['course'].queryset = Course.objects.filter(diving_center=diving_center, is_active=True, just_one_dive=True).order_by('name')
            self.fields['selected_group'].queryset = DivingGroup.objects.filter(diving_center=diving_center)
            self.fields['assigned_staff'].queryset = Staff.objects.filter(diving_center=diving_center, status='ACTIVE')
            self.fields['assigned_staff'].empty_label = "Selecciona un instructor (opcional)"

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
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'special_requirements': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'difficulty_level': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'depth_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'depth_max': forms.NumberInput(attrs={'class': 'form-control'}),            
            

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
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.ChoiceField(choices=Customer.COUNTRY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    contact_person = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)


    
    arrival_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        required=True
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        required=True
    )


    
    group_size = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
        help_text='Número de personas en este grupo'
    )

    class Meta:
        model = DivingGroup
        fields = (
            'name', 'country', 'contact_person', 'email',
            'phone', 'description', 'arrival_date', 'departure_date', 'group_size'
        )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arrival_date = self.initial.get('arrival_date') or self.instance.arrival_date
        if arrival_date:
            self.initial['arrival_date'] = arrival_date.strftime('%Y-%m-%d')

        departure_date = self.initial.get('departure_date') or self.instance.departure_date
        if departure_date:
            self.initial['departure_date'] = departure_date.strftime('%Y-%m-%d')

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
        fields = (
            'first_name', 'last_name', 'email', 'phone_number', 'certification_level',
            'certification_number', 'languages', 'experience_years', 'specialties',
            'hire_date', 'status', 'hourly_rate', 'profile_picture', 'notes'
        )
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'specialties': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'languages': forms.TextInput(attrs={'placeholder': 'e.g., English, Spanish, French'}),
            'hourly_rate': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()

class MedicalForm(forms.ModelForm):
    """Form for external users to fill medical information"""
    
    # Medical questionnaire fields - all the radio button questions
    pregunta_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}) , required=True)
    pregunta_1_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_1_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_1_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_1_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    
    pregunta_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    pregunta_2_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_2_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_2_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_2_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    
    pregunta_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    
    pregunta_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    pregunta_4_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_4_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_4_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_4_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    
    pregunta_5 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    
    pregunta_6 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    pregunta_6_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_6_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_6_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_6_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_6_5 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    
    pregunta_7 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    pregunta_7_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_7_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_7_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_7_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    
    pregunta_8 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    pregunta_8_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_8_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_8_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_8_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_8_5 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    
    pregunta_9 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)
    pregunta_9_1 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_9_2 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_9_3 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_9_4 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_9_5 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    pregunta_9_6 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=False)
    
    pregunta_10 = forms.ChoiceField(choices=[('1', 'Sí'), ('0', 'No')], widget=forms.RadioSelect(attrs={'class': 'radio-option'}), required=True)

    class Meta:
        model = Customer
        fields = (
            'first_name', 'last_name', 'email', 'phone_number', 'country', 'language',
            'birthday', 'certification_level', 'emergency_contact', 'medical_conditions',
            'weight', 'height', 'foot_size', 'default_tank_size', 'swimming_ability'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control','required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control','required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control','required': True}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control','required': True}),
            'country': forms.Select(choices=Customer.COUNTRY_CHOICES, attrs={'class': 'form-control','required': True}),
            'language': forms.Select(
                choices=[
                    ('EN', 'English'),
                    ('ES', 'Español'),
                    ('FR', 'Français'),
                    ('DE', 'Deutsch'),
                    ('NL', 'Nederlands'),
                    ('CAT', 'Català'),
                ],
                attrs={'class': 'form-control', 'id': 'language-select','required': True}
            ),
            'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'certification_level': forms.Select(choices=Customer.DIVING_LEVEL_CHOICES, attrs={'class': 'form-control','required': True}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control','required': True}),
            'medical_conditions': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Please provide additional medical information or details about any conditions mentioned above...'
            }),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'kg', 'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'cm', 'class': 'form-control'}),
            'foot_size': forms.NumberInput(attrs={'step': '0.5', 'placeholder': 'EU size', 'class': 'form-control'}),
            'default_tank_size': forms.Select(attrs={'class': 'form-control','required': True}),
            'swimming_ability': forms.Select(attrs={'class': 'form-control','required': True}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Store all medical questionnaire answers in JSON field
        medical_answers = {}
        for field_name in self.fields:
            if field_name.startswith('pregunta_'):
                value = self.cleaned_data.get(field_name)
                if value:
                    medical_answers[field_name] = value == '1'  # Convert to boolean
        
        instance.medical_questionnaire_answers = medical_answers
        
        if commit:
            instance.save()
        return instance

class CourseForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    course_type = forms.ChoiceField(choices=Course.COURSE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    total_dives = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    duration_days = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.DecimalField(decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    prerequisites = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), required=False)
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    just_one_dive = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    includes_material = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    includes_instructor = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    includes_insurance = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = Course
        fields = [
            'name', 'course_type', 'description', 'total_dives', 'duration_days',
            'price', 'prerequisites', 'is_active', 'just_one_dive',
            'includes_material', 'includes_instructor', 'includes_insurance'
        ]

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
            self.fields['primary_instructor'].empty_label = "Selecciona un instructor (opcional)"

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
            self.fields['instructor'].empty_label = "Seleciona un instructor (opcional)"

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
            empty_label="Selecciona una salida",
            widget=forms.Select(attrs={'class': 'form-control'}),
            help_text="Selecciona una salida para esta lección"
        )

        # Add primary instructor field
        instructors = Staff.objects.filter(
            diving_center=diving_center,
            status='ACTIVE'
        )

        self.fields['instructor'] = forms.ModelChoiceField(
            queryset=instructors,
            required=False,
            empty_label="Selecciona el instructor principal",
            widget=forms.Select(attrs={'class': 'form-control'}),
            initial=session.enrollment.primary_instructor,
            help_text="Instructor principal para esta lección"
        )

        # Add assistant instructors field
        self.fields['assistant_instructors'] = forms.ModelMultipleChoiceField(
            queryset=instructors,
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            help_text="Miembros del personal que ayudarán en esta lección"
        )

        # Add session notes field
        self.fields['instructor_notes'] = forms.CharField(
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            required=False,
            help_text="Notas del instructor sobre esta lección"
        )

class LessonCompletionForm(forms.Form):
    GRADE_CHOICES = [
        ('PASS', 'Aprovado'),
        ('FAIL', 'Suspendido'),
        ('EXCELLENT', 'Excelente'),
        ('GOOD', 'Bueno'),
        ('SATISFACTORY', 'Satisfactorio'),
        ('NEEDS_IMPROVEMENT', 'Necesita mejorar'),
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

class ScheduleMultipleSessionsForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'course-filter'}),
        label='Curso',
        help_text='Selecciona el curso para filtrar las sesiones'
    )

    session_number = forms.IntegerField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'session-filter'}),
        label='Número de Sesión',
        help_text='Selecciona el número de sesión',
        required=False
    )

    sessions = forms.ModelMultipleChoiceField(
        queryset=CourseSession.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'session-checkbox'}),
        label='Sesiones Pendientes',
        help_text='Selecciona las sesiones que quieres programar'
    )

    dive_schedule = forms.ModelChoiceField(
        queryset=DiveSchedule.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Salida',
        help_text='Selecciona la salida donde programar las sesiones'
    )

    instructor = forms.ModelChoiceField(
        queryset=Staff.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Instructor',
        help_text='Instructor para las sesiones (opcional)'
    )

    def __init__(self, diving_center=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['course'].queryset = Course.objects.filter(
                diving_center=diving_center, 
                is_active=True
            ).order_by('name')
            
            # Get future dive schedules
            from datetime import date
            self.fields['dive_schedule'].queryset = DiveSchedule.objects.filter(
                diving_center=diving_center,
                date__gte=date.today()
            ).order_by('date', 'time')
            
            self.fields['instructor'].queryset = Staff.objects.filter(
                diving_center=diving_center, 
                status='ACTIVE'
            )
            self.fields['instructor'].empty_label = "Selecciona un instructor (opcional)"

        # Initialize session_number choices
        self.fields['session_number'].widget = forms.Select(
            choices=[(i, f'Sesión {i}') for i in range(1, 11)],
            attrs={'class': 'form-control', 'id': 'session-filter'}
        )

class MultipleCustomerEnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'course-select'}),
        label='Curso/Actividad',
        help_text='Selecciona el curso o actividad'
    )

    customers = forms.ModelMultipleChoiceField(
        queryset=Customer.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'customer-checkbox'}),
        label='Clientes',
        help_text='Selecciona los clientes para inscribir'
    )

    # primary_instructor = forms.ModelChoiceField(
    #     queryset=Staff.objects.none(),
    #     required=False,
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     label='Instructor Principal',
    #     help_text='Instructor principal para este curso (opcional)'
    # )

    # start_date = forms.DateField(
    #     widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    #     required=False,
    #     label='Fecha de Inicio',
    #     help_text='Fecha de inicio del curso (opcional)'
    # )

    # price_paid = forms.DecimalField(
    #     widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    #     required=False,
    #     label='Precio Pagado',
    #     help_text='Precio pagado por cada cliente (opcional)'
    # )

    # is_paid = forms.BooleanField(
    #     required=False,
    #     widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    #     label='Marcado como Pagado'
    # )

    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label='Notas',
        help_text='Notas adicionales para la inscripción'
    )

    def __init__(self, diving_center=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if diving_center:
            self.fields['course'].queryset = Course.objects.filter(
                diving_center=diving_center, 
                is_active=True
            ).order_by('name')
            self.fields['customers'].queryset = Customer.objects.filter(
                diving_center=diving_center
            ).order_by('first_name', 'last_name')
            # self.fields['primary_instructor'].queryset = Staff.objects.filter(
            #     diving_center=diving_center, 
            #     status='ACTIVE'
            # )
            # self.fields['primary_instructor'].empty_label = "Selecciona un instructor (opcional)"
