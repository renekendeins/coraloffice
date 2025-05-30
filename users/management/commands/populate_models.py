
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import (
    UserProfile, Customer, DiveActivity, DivingSite, DiveSchedule, 
    CustomerDiveActivity, InventoryItem, DivingGroup, DivingGroupMember
)
from datetime import date, time, datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Populate all models with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate models...')
        
        # Create diving centers
        diving_centers = self.create_diving_centers()
        
        # Create customers
        customers = self.create_customers(diving_centers)
        
        # Create diving activities
        activities = self.create_activities(diving_centers)
        
        # Create diving sites
        sites = self.create_diving_sites(diving_centers)
        
        # Create dive schedules
        schedules = self.create_dive_schedules(diving_centers, sites, activities)
        
        # Create customer dive activities
        self.create_customer_dive_activities(customers, schedules, activities)
        
        # Create inventory items
        self.create_inventory_items(diving_centers)
        
        # Create diving groups
        groups = self.create_diving_groups(diving_centers)
        
        # Create group members
        self.create_group_members(groups, customers)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated models with sample data!')
        )

    def create_diving_centers(self):
        centers = []
        center_names = [
            'divecenter1', 'divecenter2', 'divecenter3', 'divecenter4', 'divecenter5',
            'divecenter6', 'divecenter7', 'divecenter8', 'divecenter9', 'divecenter10'
        ]
        
        for i, name in enumerate(center_names, 1):
            if not User.objects.filter(username=name).exists():
                user = User.objects.create_user(
                    username=name,
                    email=f'{name}@example.com',
                    password='password123',
                    first_name=f'Dive Center {i}',
                    last_name='Management'
                )
                user.userprofile.is_diving_center = True
                user.userprofile.business_name = f'Dive Center {i} Ltd'
                user.userprofile.business_license = f'DC{i:03d}-2024'
                user.userprofile.location = random.choice(['Maldives', 'Egypt', 'Thailand', 'Indonesia', 'Philippines'])
                user.userprofile.save()
                centers.append(user)
                self.stdout.write(f'Created diving center: {name}')
            else:
                centers.append(User.objects.get(username=name))
        
        return centers

    def create_customers(self, diving_centers):
        customers = []
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa', 
            'Robert', 'Maria', 'James', 'Anna', 'Daniel', 'Sophie', 'Mark', 'Laura',
            'Peter', 'Julia', 'Thomas', 'Elena', 'Andrew', 'Kate', 'Ryan', 'Nicole',
            'Kevin', 'Amy', 'Brian', 'Rachel', 'Steven', 'Jessica'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson'
        ]
        
        countries = [choice[0] for choice in Customer.COUNTRY_CHOICES]
        languages = [choice[0] for choice in Customer.LANGUAGE_CHOICES]
        cert_levels = [choice[0] for choice in Customer.DIVING_LEVEL_CHOICES]
        
        for center in diving_centers:
            for i in range(15):  # 15 customers per center = 150 total
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                customer = Customer.objects.create(
                    diving_center=center,
                    first_name=first_name,
                    last_name=last_name,
                    email=f'{first_name.lower()}.{last_name.lower()}{i}@email.com',
                    phone_number=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    country=random.choice(countries),
                    language=random.choice(languages),
                    birthday=date(
                        random.randint(1970, 2005),
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ),
                    certification_level=random.choice(cert_levels),
                    emergency_contact=f'Emergency Contact {i}',
                    medical_conditions=random.choice([
                        '', 'None', 'Mild asthma', 'Allergic to seafood', 
                        'Previous knee surgery', 'Controlled diabetes'
                    ]),
                    weight=random.uniform(50, 100),
                    height=random.uniform(150, 195),
                    foot_size=random.uniform(35, 46)
                )
                customers.append(customer)
        
        self.stdout.write(f'Created {len(customers)} customers')
        return customers

    def create_activities(self, diving_centers):
        activities = []
        activity_types = [
            ('Try Dive', 'Introductory dive for beginners', 60, 45.00),
            ('Single Dive', 'Single recreational dive', 45, 35.00),
            ('Double Dive', 'Two dives in one trip', 120, 65.00),
            ('Night Dive', 'Guided night diving experience', 60, 50.00),
            ('Deep Dive', 'Deep water diving', 75, 55.00),
            ('Open Water Course', 'PADI Open Water certification', 480, 350.00),
            ('Advanced Course', 'Advanced Open Water certification', 360, 280.00),
            ('Rescue Course', 'Rescue Diver certification', 600, 450.00),
            ('Wreck Dive', 'Shipwreck exploration dive', 90, 70.00),
            ('Drift Dive', 'Current diving experience', 60, 60.00)
        ]
        
        for center in diving_centers:
            for name, desc, duration, price in activity_types:
                activity, created = DiveActivity.objects.get_or_create(
                    diving_center=center,
                    name=name,
                    defaults={
                        'description': desc,
                        'duration_minutes': duration,
                        'price': price
                    }
                )
                if created:
                    activities.append(activity)
        
        self.stdout.write(f'Created {len(activities)} activities')
        return activities

    def create_diving_sites(self, diving_centers):
        sites = []
        site_data = [
            ('Coral Garden', 'Beautiful coral formations', 5, 18, 'BEGINNER'),
            ('Blue Hole', 'Deep blue water diving', 15, 40, 'ADVANCED'),
            ('Shark Point', 'Shark observation site', 8, 25, 'INTERMEDIATE'),
            ('Wreck Site Alpha', 'Sunken ship exploration', 12, 30, 'INTERMEDIATE'),
            ('Drift Corner', 'Strong current diving', 10, 35, 'ADVANCED'),
            ('Turtle Bay', 'Sea turtle sanctuary', 6, 20, 'BEGINNER'),
            ('Cave System', 'Underwater cave diving', 18, 45, 'EXPERT'),
            ('Reef Wall', 'Vertical reef wall', 8, 28, 'INTERMEDIATE'),
            ('Pinnacle Rock', 'Rocky pinnacle formation', 12, 32, 'INTERMEDIATE'),
            ('Manta Station', 'Manta ray cleaning station', 10, 25, 'BEGINNER')
        ]
        
        for center in diving_centers:
            for name, desc, min_depth, max_depth, difficulty in site_data:
                site = DivingSite.objects.create(
                    diving_center=center,
                    name=name,
                    location=f'{name} Location - {center.userprofile.location}',
                    depth_min=min_depth,
                    depth_max=max_depth,
                    difficulty_level=difficulty,
                    description=desc,
                    special_requirements=random.choice([
                        '', 'Advanced certification required', 'Good buoyancy control needed',
                        'Strong swimming skills required', 'Previous deep diving experience'
                    ])
                )
                sites.append(site)
        
        self.stdout.write(f'Created {len(sites)} diving sites')
        return sites

    def create_dive_schedules(self, diving_centers, sites, activities):
        schedules = []
        start_date = date.today()
        
        for center in diving_centers:
            center_sites = [site for site in sites if site.diving_center == center]
            center_activities = [act for act in activities if act.diving_center == center]
            
            for i in range(15):  # 15 schedules per center
                dive_date = start_date + timedelta(days=random.randint(-30, 60))
                dive_time = time(
                    random.choice([7, 8, 9, 10, 14, 15, 16]),
                    random.choice([0, 30])
                )
                
                schedule = DiveSchedule.objects.create(
                    diving_center=center,
                    date=dive_date,
                    time=dive_time,
                    dive_site=random.choice(center_sites),
                    max_participants=random.randint(6, 20),
                    description=f'Scheduled dive {i+1}',
                    special_notes=random.choice([
                        '', 'Bring underwater camera', 'Check weather conditions',
                        'Early arrival required', 'Equipment check mandatory'
                    ]),
                    activity=random.choice(center_activities) if random.choice([True, False]) else None
                )
                schedules.append(schedule)
        
        self.stdout.write(f'Created {len(schedules)} dive schedules')
        return schedules

    def create_customer_dive_activities(self, customers, schedules, activities):
        participations = []
        tank_sizes = [choice[0] for choice in CustomerDiveActivity.TANK_SIZE_CHOICES]
        statuses = [choice[0] for choice in CustomerDiveActivity.STATUS_CHOICES]
        
        for schedule in schedules:
            # Add 2-8 participants per dive
            num_participants = random.randint(2, 8)
            center_customers = [c for c in customers if c.diving_center == schedule.diving_center]
            selected_customers = random.sample(center_customers, min(num_participants, len(center_customers)))
            center_activities = [a for a in activities if a.diving_center == schedule.diving_center]
            
            for customer in selected_customers:
                participation = CustomerDiveActivity.objects.create(
                    customer=customer,
                    dive_schedule=schedule,
                    activity=random.choice(center_activities),
                    tank_size=random.choice(tank_sizes),
                    needs_wetsuit=random.choice([True, False]),
                    needs_bcd=random.choice([True, False]),
                    needs_regulator=random.choice([True, False]),
                    needs_guide=random.choice([True, False]),
                    needs_insurance=random.choice([True, False]),
                    status=random.choice(statuses),
                    has_arrived=random.choice([True, False]),
                    is_paid=random.choice([True, False])
                )
                participations.append(participation)
        
        self.stdout.write(f'Created {len(participations)} customer dive activities')
        return participations

    def create_inventory_items(self, diving_centers):
        items = []
        inventory_data = [
            ('5mm Wetsuit', 'WETSUIT', 'XS', 5, 5),
            ('5mm Wetsuit', 'WETSUIT', 'S', 8, 7),
            ('5mm Wetsuit', 'WETSUIT', 'M', 12, 10),
            ('5mm Wetsuit', 'WETSUIT', 'L', 10, 8),
            ('5mm Wetsuit', 'WETSUIT', 'XL', 6, 5),
            ('BCD Vest', 'BCD', 'S', 6, 6),
            ('BCD Vest', 'BCD', 'M', 10, 9),
            ('BCD Vest', 'BCD', 'L', 8, 7),
            ('BCD Vest', 'BCD', 'XL', 4, 4),
            ('Regulator Set', 'REGULATOR', 'N/A', 15, 14),
            ('Fins', 'FINS', 'S', 8, 7),
            ('Fins', 'FINS', 'M', 12, 10),
            ('Fins', 'FINS', 'L', 10, 8),
            ('Diving Mask', 'MASK', 'N/A', 20, 18),
            ('Diving Boots', 'BOOTS', 'S', 6, 5),
            ('Diving Boots', 'BOOTS', 'M', 8, 7),
            ('Diving Boots', 'BOOTS', 'L', 6, 5),
            ('12L Tank', 'TANK', 'N/A', 20, 18),
            ('15L Tank', 'TANK', 'N/A', 10, 9),
            ('Weight Belt', 'WEIGHT', 'N/A', 15, 14)
        ]
        
        conditions = [choice[0] for choice in InventoryItem._meta.get_field('condition').choices]
        
        for center in diving_centers:
            for name, category, size, total, available in inventory_data:
                item = InventoryItem.objects.create(
                    diving_center=center,
                    name=name,
                    category=category,
                    size=size,
                    quantity_total=total,
                    quantity_available=available,
                    condition=random.choice(conditions),
                    purchase_date=date.today() - timedelta(days=random.randint(30, 1000)),
                    last_maintenance=date.today() - timedelta(days=random.randint(1, 90)) if random.choice([True, False]) else None,
                    notes=random.choice(['', 'Needs maintenance soon', 'Recently serviced', 'Good condition'])
                )
                items.append(item)
        
        self.stdout.write(f'Created {len(items)} inventory items')
        return items

    def create_diving_groups(self, diving_centers):
        groups = []
        group_names = [
            'Ocean Explorers', 'Deep Blue Divers', 'Coral Seekers', 'Marine Adventurers',
            'Aqua Nomads', 'Blue Planet Team', 'Sea Wanderers', 'Dive Masters Club',
            'Underwater Photographers', 'Reef Guardians', 'Depth Hunters', 'Current Riders',
            'Blue Water Society', 'Marine Life Enthusiasts', 'Wreck Explorers'
        ]
        
        countries = [choice[0] for choice in Customer.COUNTRY_CHOICES]
        
        for center in diving_centers:
            for i in range(8):  # 8 groups per center
                group_name = random.choice(group_names)
                group = DivingGroup.objects.create(
                    diving_center=center,
                    name=f'{group_name} {i+1}',
                    country=random.choice(countries),
                    contact_person=f'Contact Person {i+1}',
                    email=f'group{i+1}@{group_name.lower().replace(" ", "")}.com',
                    phone=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    description=f'A group of diving enthusiasts from {group_name}',
                    arrival_date=date.today() + timedelta(days=random.randint(-10, 30)),
                    departure_date=date.today() + timedelta(days=random.randint(31, 60))
                )
                groups.append(group)
        
        self.stdout.write(f'Created {len(groups)} diving groups')
        return groups

    def create_group_members(self, groups, customers):
        memberships = []
        
        for group in groups:
            # Each group has 3-8 members
            num_members = random.randint(3, 8)
            center_customers = [c for c in customers if c.diving_center == group.diving_center]
            selected_customers = random.sample(center_customers, min(num_members, len(center_customers)))
            
            for i, customer in enumerate(selected_customers):
                membership = DivingGroupMember.objects.create(
                    group=group,
                    customer=customer,
                    is_leader=(i == 0)  # First member is the leader
                )
                memberships.append(membership)
        
        self.stdout.write(f'Created {len(memberships)} group memberships')
        return memberships
