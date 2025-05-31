from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
        return f"{self.user.username}'s Profile"

class Customer(models.Model):
    DIVING_LEVEL_CHOICES = [
        ('NONE', 'No certification'),
        ('BEGINNER', 'Beginner'),
        ('OPEN_WATER', 'Open Water'),
        ('ADVANCED_OPEN_WATER', 'Advanced Open Water'),
        ('RESCUE_DIVER', 'Rescue Diver'),
        ('DIVEMASTER', 'Divemaster'),
        ('INSTRUCTOR', 'Instructor'),
    ]
    
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('ES', 'Spanish'),
        ('FR', 'French'),
        ('DE', 'German'),
        ('IT', 'Italian'),
        ('PT', 'Portuguese'),
        ('RU', 'Russian'),
        ('ZH', 'Chinese'),
        ('JA', 'Japanese'),
        ('OTHER', 'Other'),
    ]
    
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('GB', 'United Kingdom'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('PT', 'Portugal'),
        ('NL', 'Netherlands'),
        ('BE', 'Belgium'),
        ('CH', 'Switzerland'),
        ('AT', 'Austria'),
        ('SE', 'Sweden'),
        ('NO', 'Norway'),
        ('DK', 'Denmark'),
        ('FI', 'Finland'),
        ('AU', 'Australia'),
        ('NZ', 'New Zealand'),
        ('JP', 'Japan'),
        ('KR', 'South Korea'),
        ('CN', 'China'),
        ('IN', 'India'),
        ('BR', 'Brazil'),
        ('AR', 'Argentina'),
        ('MX', 'Mexico'),
        ('RU', 'Russia'),
        ('ZA', 'South Africa'),
        ('EG', 'Egypt'),
        ('TH', 'Thailand'),
        ('ID', 'Indonesia'),
        ('MY', 'Malaysia'),
        ('SG', 'Singapore'),
        ('PH', 'Philippines'),
        ('VN', 'Vietnam'),
        ('OTHER', 'Other'),
    ]
    
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='OTHER')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='EN')
    birthday = models.DateField(null=True, blank=True)
    certification_level = models.CharField(max_length=50, choices=DIVING_LEVEL_CHOICES, default='NONE')
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_conditions = models.TextField(blank=True)
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    foot_size = models.FloatField(null=True, blank=True, help_text="Foot size (EU)")
    default_tank_size = models.CharField(max_length=10, choices=[
        ('10L', '10 Liters'),
        ('12L', '12 Liters'),
        ('15L', '15 Liters'),
        ('18L', '18 Liters'),
    ], default='12L', help_text="Default tank size for this customer")
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
            return "Not calculated"
        
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
            return "Not calculated"
        
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
            return "Not calculated"
        
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
            return "Not calculated"
        
        # Direct EU size mapping for boots
        return f"EU {int(self.foot_size)}"

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
    depth_min = models.FloatField(help_text="Minimum depth in meters")
    depth_max = models.FloatField(help_text="Maximum depth in meters")
    difficulty_level = models.CharField(max_length=20, choices=[
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
        ('EXPERT', 'Expert'),
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
    special_notes = models.TextField(blank=True, help_text="Special requirements or important notes for this dive")
    created_at = models.DateTimeField(auto_now_add=True)
    #activity = models.ForeignKey(DiveActivity, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Dive at {self.dive_site} - {self.date} at {self.time}"

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
        ('10L', '10 Liters'),
        ('12L', '12 Liters'),
        ('15L', '15 Liters'),
        ('18L', '18 Liters'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ON_BOARD', 'On Board'),
        ('BACK_ON_BOAT', 'Back on Boat'),
        ('DEPARTED', 'Departed'),
        ('FINISHED', 'Finished'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='dive_activities')
    dive_schedule = models.ForeignKey(DiveSchedule, on_delete=models.CASCADE, related_name='customer_activities')
    activity = models.ForeignKey(DiveActivity, on_delete=models.CASCADE, related_name='customer_bookings')
    tank_size = models.CharField(max_length=10, choices=TANK_SIZE_CHOICES, default='12L')
    needs_wetsuit = models.BooleanField(default=False)
    needs_bcd = models.BooleanField(default=False)
    needs_regulator = models.BooleanField(default=False)
    needs_guide = models.BooleanField(default=False)
    needs_insurance = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    has_arrived = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'dive_schedule']

    def __str__(self):
        return f"{self.customer} - {self.activity.name}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('WETSUIT', 'Wetsuit'),
        ('BCD', 'BCD'),
        ('REGULATOR', 'Regulator'),
        ('FINS', 'Fins'),
        ('MASK', 'Mask'),
        ('BOOTS', 'Boots'),
        ('TANK', 'Tank'),
        ('WEIGHT', 'Weight'),
        ('OTHER', 'Other'),
    ]
    
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
        ('N/A', 'Not Applicable'),
    ]
    
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='N/A')
    quantity_total = models.IntegerField(default=1)
    quantity_available = models.IntegerField(default=1)
    condition = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('OUT_OF_SERVICE', 'Out of Service'),
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

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()