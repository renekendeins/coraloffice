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
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    certification_level = models.CharField(max_length=50, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class DiveActivity(models.Model):
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dive_activities')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DiveSchedule(models.Model):
    diving_center = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dive_schedules')
    date = models.DateField()
    time = models.TimeField()
    dive_site = models.CharField(max_length=100)
    max_participants = models.IntegerField(default=46)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activity = models.ForeignKey(DiveActivity, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Dive at {self.dive_site} - {self.date} at {self.time}"

    def get_participants(self):
        """Get all customers participating in this dive"""
        return Customer.objects.filter(customerdiveactivity__dive_schedule=self)

    def get_participant_count(self):
        """Get the count of participants for this dive"""
        return self.customerdiveactivity_set.count()

class CustomerDiveActivity(models.Model):
    TANK_SIZE_CHOICES = [
        ('10L', '10 Liters'),
        ('12L', '12 Liters'),
        ('15L', '15 Liters'),
        ('18L', '18 Liters'),
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'dive_schedule']

    def __str__(self):
        return f"{self.customer} - {self.activity.name}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()