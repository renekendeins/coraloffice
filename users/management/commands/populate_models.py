
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import (
    UserProfile, Customer, DiveActivity, DivingSite, DiveSchedule, 
    CustomerDiveActivity, InventoryItem, DivingGroup, DivingGroupMember
)
from datetime import date, time, timedelta
import random

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate models...')
        
        # Create diving center users
        diving_centers = []
        for i in range(3):
            username = f'divecenter{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'center{i+1}@example.com',
                    password='password123',
                    first_name=f'Dive Center {i+1}',
                    last_name='Owner'
                )
                user.userprofile.is_diving_center = True
                user.userprofile.business_name = f'Ocean Adventures {i+1}'
                user.userprofile.business_license = f'DC{i+1:03d}'
                user.userprofile.save()
                diving_centers.append(user)
                self.stdout.write(f'Created diving center: {username}')
            else:
                diving_centers.append(User.objects.get(username=username))

        # Create diving sites
        sites_data = [
            {'name': 'Coral Garden', 'location': 'North Bay', 'depth_min': 5, 'depth_max': 18, 'difficulty': 'BEGINNER'},
            {'name': 'Blue Hole', 'location': 'East Coast', 'depth_min': 15, 'depth_max': 40, 'difficulty': 'ADVANCED'},
            {'name': 'Wreck Explorer', 'location': 'South Point', 'depth_min': 12, 'depth_max': 25, 'difficulty': 'INTERMEDIATE'},
            {'name': 'Cave Adventure', 'location': 'West Shore', 'depth_min': 8, 'depth_max': 30, 'difficulty': 'EXPERT'},
            {'name': 'Night Dive Spot', 'location': 'Central Bay', 'depth_min': 6, 'depth_max': 20, 'difficulty': 'INTERMEDIATE'},
        ]

        for center in diving_centers:
            for site_data in sites_data:
                if not DivingSite.objects.filter(diving_center=center, name=site_data['name']).exists():
                    DivingSite.objects.create(
                        diving_center=center,
                        name=site_data['name'],
                        location=site_data['location'],
                        depth_min=site_data['depth_min'],
                        depth_max=site_data['depth_max'],
                        difficulty_level=site_data['difficulty'],
                        description=f"Beautiful diving site at {site_data['location']}"
                    )

        # Create dive activities
        activities_data = [
            {'name': 'Discover Scuba', 'description': 'Introduction to scuba diving', 'duration': 120, 'price': 85.00},
            {'name': 'Open Water Dive', 'description': 'Standard recreational dive', 'duration': 90, 'price': 65.00},
            {'name': 'Advanced Dive', 'description': 'Deep water exploration', 'duration': 100, 'price': 75.00},
            {'name': 'Night Dive', 'description': 'Underwater night experience', 'duration': 80, 'price': 80.00},
            {'name': 'Wreck Dive', 'description': 'Explore sunken vessels', 'duration': 110, 'price': 90.00},
        ]

        for center in diving_centers:
            for activity_data in activities_data:
                if not DiveActivity.objects.filter(diving_center=center, name=activity_data['name']).exists():
                    DiveActivity.objects.create(
                        diving_center=center,
                        name=activity_data['name'],
                        description=activity_data['description'],
                        duration_minutes=activity_data['duration'],
                        price=activity_data['price']
                    )

        # Create customers
        customers_data = [
            {'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@email.com', 'country': 'US', 'language': 'EN', 'cert': 'OPEN_WATER'},
            {'first_name': 'Maria', 'last_name': 'Garcia', 'email': 'maria.garcia@email.com', 'country': 'ES', 'language': 'ES', 'cert': 'ADVANCED_OPEN_WATER'},
            {'first_name': 'Hans', 'last_name': 'Mueller', 'email': 'hans.mueller@email.com', 'country': 'DE', 'language': 'DE', 'cert': 'BEGINNER'},
            {'first_name': 'Sophie', 'last_name': 'Dubois', 'email': 'sophie.dubois@email.com', 'country': 'FR', 'language': 'FR', 'cert': 'RESCUE_DIVER'},
            {'first_name': 'Yuki', 'last_name': 'Tanaka', 'email': 'yuki.tanaka@email.com', 'country': 'JP', 'language': 'JA', 'cert': 'DIVEMASTER'},
            {'first_name': 'Emma', 'last_name': 'Johnson', 'email': 'emma.johnson@email.com', 'country': 'AU', 'language': 'EN', 'cert': 'OPEN_WATER'},
            {'first_name': 'Lars', 'last_name': 'Andersen', 'email': 'lars.andersen@email.com', 'country': 'DK', 'language': 'EN', 'cert': 'ADVANCED_OPEN_WATER'},
            {'first_name': 'Giulia', 'last_name': 'Rossi', 'email': 'giulia.rossi@email.com', 'country': 'IT', 'language': 'IT', 'cert': 'BEGINNER'},
        ]

        all_customers = []
        for center in diving_centers:
            for customer_data in customers_data:
                if not Customer.objects.filter(diving_center=center, email=customer_data['email']).exists():
                    customer = Customer.objects.create(
                        diving_center=center,
                        first_name=customer_data['first_name'],
                        last_name=customer_data['last_name'],
                        email=customer_data['email'],
                        phone_number=f'+1-555-{random.randint(1000, 9999)}',
                        country=customer_data['country'],
                        language=customer_data['language'],
                        certification_level=customer_data['cert'],
                        birthday=date(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28)),
                        weight=random.uniform(50, 100),
                        height=random.uniform(150, 200),
                        foot_size=random.uniform(36, 46)
                    )
                    all_customers.append(customer)

        # Create diving groups
        groups_data = [
            {'name': 'German Divers Club', 'country': 'DE', 'contact': 'Klaus Weber', 'email': 'klaus@germandivers.com'},
            {'name': 'French Ocean Explorers', 'country': 'FR', 'contact': 'Pierre Moreau', 'email': 'pierre@frenchocean.fr'},
            {'name': 'Nordic Dive Team', 'country': 'NO', 'contact': 'Erik Olsen', 'email': 'erik@nordicdive.no'},
        ]

        for center in diving_centers:
            for group_data in groups_data:
                if not DivingGroup.objects.filter(diving_center=center, name=group_data['name']).exists():
                    group = DivingGroup.objects.create(
                        diving_center=center,
                        name=group_data['name'],
                        country=group_data['country'],
                        contact_person=group_data['contact'],
                        email=group_data['email'],
                        phone=f'+1-555-{random.randint(1000, 9999)}',
                        arrival_date=date.today() + timedelta(days=random.randint(1, 30)),
                        departure_date=date.today() + timedelta(days=random.randint(31, 60))
                    )
                    
                    # Add some customers to groups
                    center_customers = Customer.objects.filter(diving_center=center)
                    for customer in random.sample(list(center_customers), min(3, len(center_customers))):
                        if not DivingGroupMember.objects.filter(group=group, customer=customer).exists():
                            DivingGroupMember.objects.create(group=group, customer=customer)

        # Create dive schedules
        for center in diving_centers:
            sites = DivingSite.objects.filter(diving_center=center)
            activities = DiveActivity.objects.filter(diving_center=center)
            
            for i in range(10):  # Create 10 dives per center
                dive_date = date.today() + timedelta(days=random.randint(1, 30))
                dive_time = time(random.randint(8, 16), random.choice([0, 30]))
                
                if sites.exists() and activities.exists():
                    DiveSchedule.objects.create(
                        diving_center=center,
                        date=dive_date,
                        time=dive_time,
                        dive_site=random.choice(sites),
                        activity=random.choice(activities),
                        max_participants=random.randint(4, 12),
                        description=f"Exciting dive at {random.choice(sites).name}",
                        special_notes="Remember to bring underwater camera!" if random.choice([True, False]) else ""
                    )

        # Create inventory items
        inventory_data = [
            {'name': 'Wetsuit 3mm', 'category': 'WETSUIT', 'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL']},
            {'name': 'BCD Vest', 'category': 'BCD', 'sizes': ['XS', 'S', 'M', 'L', 'XL']},
            {'name': 'Regulator Set', 'category': 'REGULATOR', 'sizes': ['N/A']},
            {'name': 'Diving Fins', 'category': 'FINS', 'sizes': ['S', 'M', 'L', 'XL']},
            {'name': 'Diving Mask', 'category': 'MASK', 'sizes': ['S', 'M', 'L']},
            {'name': 'Diving Boots', 'category': 'BOOTS', 'sizes': ['S', 'M', 'L', 'XL']},
            {'name': 'Air Tank 12L', 'category': 'TANK', 'sizes': ['N/A']},
            {'name': 'Weight Belt', 'category': 'WEIGHT', 'sizes': ['S', 'M', 'L']},
        ]

        for center in diving_centers:
            for item_data in inventory_data:
                for size in item_data['sizes']:
                    if not InventoryItem.objects.filter(diving_center=center, name=item_data['name'], size=size).exists():
                        total_qty = random.randint(5, 20)
                        InventoryItem.objects.create(
                            diving_center=center,
                            name=item_data['name'],
                            category=item_data['category'],
                            size=size,
                            quantity_total=total_qty,
                            quantity_available=random.randint(1, total_qty),
                            condition=random.choice(['EXCELLENT', 'GOOD', 'FAIR']),
                            purchase_date=date.today() - timedelta(days=random.randint(30, 365))
                        )

        self.stdout.write(self.style.SUCCESS('Successfully populated models with sample data!'))
