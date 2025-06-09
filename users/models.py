from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_diving_center = models.BooleanField(default=False)
    business_name = models.CharField(max_length=100, blank=True)
    business_license = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}"

class Customer(models.Model):
    DIVING_LEVEL_CHOICES = [
        ('NONE', 'Ninguno'),
        ('BEGINNER', 'Scuba'),
        ('OPEN_WATER', 'Open Water'),
        ('ADVANCED_OPEN_WATER', 'Advanced'),
        ('RESCUE_DIVER', 'Rescue.'),
        ('DIVEMASTER', 'Divemaster'),
        ('INSTRUCTOR', 'Istructor'),
    ]
    
    LANGUAGE_CHOICES = [
        ('CAT', 'Català'),
        ('ES', 'Español'),
        ('FR', 'Français'),
        ('EN', 'English'),
        ('NL', 'Nederlands'),
        ('DE', 'Deutsch'),
    ]
    
    COUNTRY_CHOICES = [
        ('ES', 'España'),
        ('FR', 'Francia'),
        ('PT', 'Portugal'),
        ('IT', 'Italia'),
        ('GB', 'Reino Unido'),
        ('BE', 'Bélgica'),
        ('NL', 'Países Bajos'),
        ('CH', 'Suiza'),
        ('DE', 'Alemania'),
        ('AT', 'Austria'),
        ('SE', 'Suecia'),
        ('DK', 'Dinamarca'),
        ('NO', 'Noruega'),
        ('FI', 'Finlandia'),
        ('IN', 'India'),
        ('US', 'Estados Unidos'),
        ('CA', 'Canadá'),
        ('OTHER', 'Otro'),

    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='OTHER')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='EN')
    birthday = models.DateField(null=True, blank=True)
    certification_level = models.CharField(max_length=50, choices=DIVING_LEVEL_CHOICES, default='Ninguna')
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_conditions = models.TextField(blank=True)
    weight = models.FloatField(null=True, blank=True, help_text="Peso en kg")
    height = models.FloatField(null=True, blank=True, help_text="Alturan en cm")
    foot_size = models.FloatField(null=True, blank=True, help_text="Talla de pie (EU)")
    default_tank_size = models.CharField(max_length=10, choices=[
        ('10L', '10 Litros'),
        ('12L', '12 Litros'),
        ('15L', '15 Litros'),
        ('18L', '18 Litros'),
    ], default='12L', help_text="Botella por defecto del cliente")
    
    # File uploads
    profile_picture = models.ImageField(upload_to='customer_profiles/', null=True, blank=True)
    diving_licence = models.FileField(upload_to='customer_documents/licences/', null=True, blank=True)
    diving_insurance = models.FileField(upload_to='customer_documents/insurance/', null=True, blank=True)
    medical_check = models.FileField(upload_to='customer_documents/medical/', null=True, blank=True)
    signature = models.ImageField(upload_to='customer_signatures/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        if self.birthday:
            from datetime import date
            today = date.today()
            return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        return None
    
    def get_wetsuit_size(self):
        """Calculate wetsuit size based on height and weight"""
        if not self.height or not self.weight:
            return "No calculado"
        
        # Basic wetsuit sizing logic
        if self.height < 160:
            if self.weight < 50: return "XS"
            elif self.weight < 60: return "S"
            elif self.weight < 70: return "M"
            else: return "L"
        elif self.height < 170:
            if self.weight < 55: return "S"
            elif self.weight < 65: return "M"
            elif self.weight < 75: return "L"
            else: return "XL"
        elif self.height < 180:
            if self.weight < 60: return "M"
            elif self.weight < 70: return "L"
            elif self.weight < 80: return "XL"
            else: return "XXL"
        else:
            if self.weight < 70: return "L"
            elif self.weight < 80: return "XL"
            else: return "XXL"
    
    def get_bcd_size(self):
        """Calculate BCD size based on chest measurement approximated from height/weight"""
        if not self.height or not self.weight:
            return "No calculado"
        
        # Approximate BCD sizing
        if self.weight < 55: return "XS"
        elif self.weight < 65: return "S"
        elif self.weight < 75: return "M"
        elif self.weight < 85: return "L"
        elif self.weight < 95: return "XL"
        else: return "XXL"
    
    def get_fins_size(self):
        """Calculate fin size based on foot size"""
        if not self.foot_size:
            return "No calculado"
        
        # EU to fin size conversion
        if self.foot_size <= 36: return "XS"
        elif self.foot_size <= 38: return "S"
        elif self.foot_size <= 41: return "M"
        elif self.foot_size <= 43: return "L"
        elif self.foot_size <= 45: return "XL"
        else: return "XXL"
    
    def get_boots_size(self):
        """Calculate boots size based on foot size"""
        if not self.foot_size:
            return "No calculado"
        
        # Direct EU size mapping for boots
        return f"EU {int(self.foot_size)}"

    def get_country_name(self):
        """Get the full country name from the country code"""
        return dict(self.COUNTRY_CHOICES).get(self.country, self.country)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_certification_level(self):
        """Get the full certification name from the certification level code"""
        return dict(self.DIVING_LEVEL_CHOICES).get(self.certification_level, self.certification_level)
    
    # Medical questionnaire fields - storing as JSON for flexibility
    medical_questionnaire_answers = models.JSONField(default=dict, blank=True, help_text="Guarda las respuestas del cuestionario médico")
    swimming_ability = models.CharField(max_length=20, choices=[
        ('excellent', 'Excelente'),
        ('good', 'Bueno'),
        ('fair', 'Suficiente'),
        ('poor', 'Insuficiente'),
    ], blank=True)
    
    def get_medical_answer(self, question_key):
        """Get answer to a specific medical question"""
        return self.medical_questionnaire_answers.get(question_key, False)
    
    def set_medical_answer(self, question_key, answer):
        """Set answer to a specific medical question"""
        if not self.medical_questionnaire_answers:
            self.medical_questionnaire_answers = {}
        self.medical_questionnaire_answers[question_key] = answer
    
    def get_swimming_ability_display(self):
        """Get the display value for swimming ability"""
        swimming_choices = {
            'excellent': 'Excelente',
            'good': 'Bueno',
            'fair': 'Suficiente',
            'poor': 'Insuficiente',
        }
        return swimming_choices.get(self.swimming_ability, self.swimming_ability)
        
class DiveActivity(models.Model):
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dive_activities')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DivingSite(models.Model):
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diving_sites')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    depth_min = models.FloatField(help_text="Profundidad mínima en metros")
    depth_max = models.FloatField(help_text="Profundidad máxima en metros")
    difficulty_level = models.CharField(max_length=20, choices=[
        ('BEGINNER', 'Principiante'),
        ('INTERMEDIATE', 'Intermedio'),
        ('ADVANCED', 'Avanzado'),
        ('EXPERT', 'Experto'),
    ], default='BEGINNER')
    description = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DiveSchedule(models.Model):
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dive_schedules')
    date = models.DateField()
    time = models.TimeField()
    dive_site = models.ForeignKey(DivingSite, on_delete=models.CASCADE, related_name='scheduled_dives')
    max_participants = models.IntegerField(default=46)
    description = models.TextField(blank=True)
    special_notes = models.TextField(blank=True, help_text="Requerimientos especiales o notas adicionales para esta inmersión")
    created_at = models.DateTimeField(auto_now_add=True)
    #activity = models.ForeignKey(DiveActivity, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Inmersión en {self.dive_site} - {self.date} a la/s {self.time}"

    def get_participants(self):
        """Get all customers participating in this dive"""
        return Customer.objects.filter(customerdiveactivity__dive_schedule=self)

    def get_participant_count(self):
        """Get the count of participants for this dive"""
        return self.customer_activities.count()
    
    def has_special_notes(self):
        """Check if this dive has special notes"""
        return bool(self.special_notes.strip())

class CustomerDiveActivity(models.Model):
    TANK_SIZE_CHOICES = [
        ('10L', '10L'),
        ('12L', '12L'),
        ('15L', '15L'),
        ('EAN12L', 'NITROX 12L'),
        ('EAN15L', 'NITROX 15L'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente de llegar'),
        ('ON_BOARD', 'A bordo'),
        ('BACK_ON_BOAT', 'Back on Boat'),
        ('DEPARTED', 'En curso'),
        ('FINISHED', 'Finalizado'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='dive_activities')
    dive_schedule = models.ForeignKey(DiveSchedule, on_delete=models.CASCADE, related_name='customer_activities')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='customer_bookings', help_text="Curso/ Actividad que el cliente está realizando")
    activity = models.ForeignKey(DiveActivity, on_delete=models.CASCADE, related_name='customer_bookings', null=True, blank=True, help_text="DEPRECATED: Use course field instead")
    assigned_staff = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_activities', help_text="Instructor/guía asignado")
    course_session = models.ForeignKey('CourseSession', on_delete=models.SET_NULL, null=True, blank=True, related_name='dive_activities', help_text="Sesión del curso que está realizando el cliente")
    tank_size = models.CharField(max_length=10, choices=TANK_SIZE_CHOICES, default='12L')
    needs_wetsuit = models.BooleanField(default=False)
    needs_bcd = models.BooleanField(default=False)
    needs_regulator = models.BooleanField(default=False)
    needs_guide = models.BooleanField(default=False)    
    needs_fins = models.BooleanField(default=False)

    needs_insurance = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    has_arrived = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'dive_schedule']

    def __str__(self):
        return f"{self.customer} - {self.course.name}"
    
    def get_activity_name(self):
        """Get the activity name from course or fallback to deprecated activity field"""
        if self.course:
            return self.course.name
        elif self.activity:
            return self.activity.name
        return "Actividad desconocida"
    
    def get_activity_price(self):
        """Get the activity price from course or fallback to deprecated activity field"""
        if self.course:
            return self.course.price
        elif self.activity:
            return self.activity.price
        return 0.00
    
    def get_activity_duration(self):
        """Get the activity duration from course or fallback to deprecated activity field"""
        if self.course:
            return self.course.duration_days * 60  # Convert days to minutes for compatibility
        elif self.activity:
            return self.activity.duration_minutes
        return 60
    
    def is_course_dive(self):
        """Check if this dive is part of a course"""
        return self.course_session is not None
    
    def get_course_info(self):
        """Get course information if this is a course dive"""
        if self.course_session:
            return {
                'course_name': self.course_session.enrollment.course.name,
                'session_number': self.course_session.session_number,
                'total_sessions': self.course_session.enrollment.course.total_dives,
                'session_title': self.course_session.title
            }
        return None

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('WETSUIT', 'Traje'),
        ('BCD', 'Jacket'),
        ('REGULATOR', 'Regulador'),
        ('FINS', 'Aletas'),
        ('MASK', 'Máscara'),
        ('BOOTS', 'Escarpines'),
        ('TANK', 'Botella'),
        ('WEIGHT', 'Plomos'),
        ('OTHER', 'Otros'),
    ]
    
    SIZE_CHOICES = [
        ('XS', 'Extra pequeño'),
        ('S', 'Pequeño'),
        ('M', 'Medio'),
        ('L', 'Largo'),
        ('XL', 'Extra Largo'),
        ('XXL', 'Extra Extra Largo'),
        ('N/A', 'No Aplicable'),
    ]
    
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='N/A')
    quantity_total = models.IntegerField(default=1)
    quantity_available = models.IntegerField(default=1)
    condition = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellente'),
        ('GOOD', 'Bueno'),
        ('FAIR', 'Justo'),
        ('POOR', 'Malo'),
        ('OUT_OF_SERVICE', 'Fuera de servicio'),
    ], default='GOOD')
    purchase_date = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.size}) - {self.quantity_available}/{self.quantity_total}"

class DivingGroup(models.Model):
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diving_groups')
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=10, choices=Customer.COUNTRY_CHOICES, default='OTHER')
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    arrival_date = models.DateField(null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DivingGroupMember(models.Model):
    group = models.ForeignKey(DivingGroup, on_delete=models.CASCADE, related_name='members')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='group_memberships')
    is_leader = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['group', 'customer']

    def __str__(self):
        return f"{self.customer} in {self.group}"

class Staff(models.Model):
    CERTIFICATION_LEVEL_CHOICES = [
        ('DIVEMASTER', 'Divemaster'),
        ('INSTRUCTOR', 'Instructor'),
        ('SENIOR_INSTRUCTOR', 'Senior Instructor'),
        ('MASTER_INSTRUCTOR', 'Master Instructor'),
        ('COURSE_DIRECTOR', 'Course Director'),        
        ('SKIPPER', 'Marinero'),        
        ('CAPTAIN', 'Patrón'),        
        ('OFFICE', 'Oficinista'),



    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Activo'),
        ('INACTIVE', 'Inactivo'),
        ('ON_LEAVE', 'Ausente'),
    ]
    
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_members')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    certification_level = models.CharField(max_length=50, choices=CERTIFICATION_LEVEL_CHOICES, default='DIVEMASTER')
    certification_number = models.CharField(max_length=100, blank=True)
    languages = models.CharField(max_length=200, help_text="Idiomas que habla (separados por comas)")
    experience_years = models.IntegerField(default=0, help_text="Años de experiencia")
    specialties = models.TextField(blank=True, help_text="Especialidades o habilidades adicionales")
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Tarifa por hora")
    profile_picture = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_certification_level_display()})"

    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_activities_count(self):
        """Get total number of activities this staff member has been assigned to"""
        return self.assigned_activities.count()
    
    def get_upcoming_activities(self):
        """Get upcoming activities for this staff member"""
        from datetime import date
        return self.assigned_activities.filter(dive_schedule__date__gte=date.today()).order_by('dive_schedule__date', 'dive_schedule__time')


class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('OPEN_WATER', 'Open Water Diver'),
        ('ADVANCED_OPEN_WATER', 'Advanced Open Water'),
        ('RESCUE_DIVER', 'Rescue Diver'),
        ('DIVEMASTER', 'Divemaster'),
        ('NITROX', 'Especialidad Nitrox'),
        ('DEEP', 'Specialty Buceo Profundo'),
        ('WRECK', 'Especialidad en Pecios'),
        ('NIGHT', 'Especialidad en Buceo Nocturno'),
        ('NAVIGATION', 'Especialidad en Navegación Subacuática'),
        ('PHOTOGRAPHY', 'Especialidad en Fotografía Subacuática'),
        ('SINGLE_DIVE', 'Inmersión Simple'),
        ('DOUBLE_DIVE', 'Inmersión Doble'),
        ('TRY_DIVE', 'Bautizo de Buceo'),
        ('SCUBA_DIVER', 'Curso Scuba Diver'),
        ('DIVING_LESSON', 'Clase de Buceo'),
        ('REFRESH', 'Curso de Refresco'),
        ('CUSTOM', 'Curso Personalizado'),

    ]
    
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=100)
    course_type = models.CharField(max_length=30, choices=COURSE_TYPE_CHOICES, default='CUSTOM')
    description = models.TextField(blank=True)
    total_dives = models.IntegerField(default=1, help_text="Número total de inmersiones en este curso")
    duration_days = models.IntegerField(default=1, help_text="Duración estimada en días")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prerequisites = models.TextField(blank=True, help_text="Certificaciones o requisitos previos necesarios")
    is_active = models.BooleanField(default=True)
    just_one_dive = models.BooleanField(default=False, help_text="Marcar si esta actividad o curso es solo para una inmersión")
    includes_material = models.BooleanField(default=True, help_text="El material está incluido en el precio del curso")
    includes_instructor = models.BooleanField(default=True, help_text="El instructor está incluido en el precio del curso")
    includes_insurance = models.BooleanField(default=True, help_text="El seguro está incluido en el precio del curso")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.total_dives} dives)"
    
    class Meta:
        ordering = ['name']


class CourseEnrollment(models.Model):
    STATUS_CHOICES = [
        ('ENROLLED', 'Inscrito'),
        ('IN_PROGRESS', 'En progreso'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
        ('ON_HOLD', 'En espera'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    primary_instructor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_course_enrollments', help_text="Instructor principal para este curso")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED')
    enrollment_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True, help_text="Fecha de la primera sesión")
    completion_date = models.DateField(null=True, blank=True)
    certificate_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'course']
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.customer} - {self.course.name} ({self.status})"
    
    def get_progress_percentage(self):
        """Calculate completion percentage based on completed course sessions"""
        total_sessions = self.course_sessions.count()
        completed_sessions = self.course_sessions.filter(status='COMPLETED').count()
        if total_sessions == 0:
            return 0
        return round((completed_sessions / total_sessions) * 100)
    
    def get_completed_lessons(self):
        """Get number of completed lessons"""
        return self.course_sessions.filter(status='COMPLETED').count()
    
    def get_completed_dives(self):
        """Get number of completed dives (alias for get_completed_lessons)"""
        return self.get_completed_lessons()
    
    def get_scheduled_lessons(self):
        """Get number of scheduled lessons"""
        return self.course_sessions.filter(status__in=['SCHEDULED', 'IN_PROGRESS']).count()
    
    def get_unscheduled_lessons(self):
        """Get number of unscheduled lessons"""
        return self.course_sessions.filter(status='NOT_SCHEDULED').count()
    
    def is_active(self):
        """Check if enrollment is active (enrolled or in progress)"""
        return self.status in ['ENROLLED', 'IN_PROGRESS']
    
    def get_next_lesson(self):
        """Get the next lesson to be completed"""
        return self.course_sessions.filter(
            status__in=['NOT_SCHEDULED', 'SCHEDULED']
        ).order_by('session_number').first()
    
    def get_all_instructors(self):
        """Get all instructors involved in this course"""
        instructors = set()
        if self.primary_instructor:
            instructors.add(self.primary_instructor)
        
        for session in self.course_sessions.all():
            if session.instructor:
                instructors.add(session.instructor)
            instructors.update(session.assistant_instructors.all())
        
        return list(instructors)
    
    def auto_update_status(self):
        """Automatically update enrollment status based on lesson progress"""
        total_lessons = self.course_sessions.count()
        completed_lessons = self.get_completed_lessons()
        scheduled_lessons = self.get_scheduled_lessons()
        
        if completed_lessons == total_lessons and total_lessons > 0:
            self.status = 'COMPLETED'
            if not self.completion_date:
                from datetime import date
                self.completion_date = date.today()
        elif scheduled_lessons > 0 or completed_lessons > 0:
            if self.status == 'ENROLLED':
                self.status = 'IN_PROGRESS'
                if not self.start_date:
                    from datetime import date
                    self.start_date = date.today()
        
        self.save()


class CourseSession(models.Model):
    SESSION_TYPE_CHOICES = [
        ('THEORY', 'Sesión teórica'),
        ('POOL', 'Aguas Confinadas'),
        ('OPEN_WATER', 'Aguas Abiertas'),
        ('EXAM', 'Examen'),
        ('PRACTICAL', 'Habilidades'),
    ]
    
    STATUS_CHOICES = [
        ('NOT_SCHEDULED', 'Sin pogramar'),
        ('SCHEDULED', 'Programado'),
        ('IN_PROGRESS', 'En progrso'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
        ('RESCHEDULED', 'Reprogramado'),
    ]
    
    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name='course_sessions',
        null=True,
        blank=True
    )

    template_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='template_sessions',
        null=True,
        blank=True,
        help_text="Curso al que pertenece esta sesión plantilla"
    )

    dive_schedule = models.ForeignKey(
        DiveSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_sessions',
        help_text="Franja de inmersión en la que está programada esta lección"
    )

    session_number = models.IntegerField(
        help_text="Número de lección en el curso (1, 2, 3, etc.)"
    )

    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default='OPEN_WATER'
    )

    title = models.CharField(
        max_length=100,
        help_text="Título de la lección (p. ej. 'Habilidades en piscina', 'Inmersión de navegación')"
    )

    description = models.TextField(
        blank=True
    )

    skills_covered = models.TextField(
        blank=True,
        help_text="Habilidades que se practicarán en esta lección"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NOT_SCHEDULED'
    )

    instructor = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_sessions',
        help_text="Instructor principal de esta lección específica"
    )

    assistant_instructors = models.ManyToManyField(
        Staff,
        blank=True,
        related_name='assisting_sessions',
        help_text="Miembros del personal que ayudan en esta lección"
    )

    scheduled_date = models.DateField(
        null=True,
        blank=True
    )

    scheduled_time = models.TimeField(
        null=True,
        blank=True
    )

    completion_date = models.DateTimeField(
        null=True,
        blank=True
    )

    grade = models.CharField(
        max_length=10,
        blank=True,
        help_text="Nota o resultado (aprobado/suspenso)"
    )

    instructor_notes = models.TextField(
        blank=True
    )

    student_feedback = models.TextField(
        blank=True,
        help_text="Comentarios del estudiante sobre esta lección"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:
        ordering = ['enrollment', 'session_number']
        unique_together = ['enrollment', 'session_number']

    def __str__(self):
        return f"{self.enrollment} - Lesson {self.session_number}: {self.title}"
    
    def is_dive_session(self):
        """Check if this session involves diving"""
        return self.session_type in ['POOL', 'OPEN_WATER']
    
    def get_location_name(self):
        """Get the location name for this session"""
        if self.dive_schedule and self.dive_schedule.dive_site:
            return self.dive_schedule.dive_site.name
        elif self.session_type == 'POOL':
            return 'Pool'
        elif self.session_type == 'THEORY':
            return 'Classroom'
        return 'Not Scheduled'
    
    def is_scheduled(self):
        """Check if this lesson is scheduled"""
        return self.dive_schedule is not None and self.status != 'NOT_SCHEDULED'
    
    def get_all_staff(self):
        """Get all staff members involved in this lesson"""
        staff_list = []
        if self.instructor:
            staff_list.append(self.instructor)
        staff_list.extend(self.assistant_instructors.all())
        return staff_list
    
    def can_be_completed(self):
        """Check if this lesson can be marked as completed"""
        return self.status in ['SCHEDULED', 'IN_PROGRESS'] and self.dive_schedule is not None

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()