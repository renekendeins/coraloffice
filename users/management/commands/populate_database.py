
import random
import string
from datetime import date, time, datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from users.models import (
    UserProfile, Customer, DiveActivity, DivingSite, DiveSchedule, 
    CustomerDiveActivity, InventoryItem, DivingGroup, DivingGroupMember
)

class Command(BaseCommand):
    help = 'Populate database with random sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--centers',
            type=int,
            default=5,
            help='Number of diving centers to create (default: 5)'
        )
        parser.add_argument(
            '--customers-per-center',
            type=int,
            default=20,
            help='Number of customers per diving center (default: 20)'
        )
        parser.add_argument(
            '--schedules-per-center',
            type=int,
            default=15,
            help='Number of dive schedules per center (default: 15)'
        )
        parser.add_argument(
            '--groups-per-center',
            type=int,
            default=8,
            help='Number of diving groups per center (default: 8)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting database population...')
        
        try:
            with transaction.atomic():
                # Create diving centers
                diving_centers = self.create_diving_centers(options['centers'])
                
                # Create customers
                customers = self.create_customers(diving_centers, options['customers_per_center'])
                
                # Create diving activities
                activities = self.create_activities(diving_centers)
                
                # Create diving sites
                sites = self.create_diving_sites(diving_centers)
                
                # Create dive schedules
                schedules = self.create_dive_schedules(diving_centers, sites, activities, options['schedules_per_center'])
                
                # Create customer dive activities
                self.create_customer_dive_activities(customers, schedules, activities)
                
                # Create inventory items
                self.create_inventory_items(diving_centers)
                
                # Create diving groups
                groups = self.create_diving_groups(diving_centers, options['groups_per_center'])
                
                # Create group members
                self.create_group_members(groups, customers)
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully populated database with random data!')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error populating database: {str(e)}')
            )

    def generate_random_string(self, length=8):
        """Generate random string for unique identifiers"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def create_diving_centers(self, count):
        centers = []
        locations = [
            'Maldives', 'Egypt', 'Thailand', 'Indonesia', 'Philippines',
            'Mexico', 'Australia', 'Costa Rica', 'Spain', 'Greece',
            'Croatia', 'Malta', 'Cyprus', 'Turkey', 'Belize'
        ]
        
        for i in range(count):
            unique_id = self.generate_random_string()
            username = f'divecenter_{unique_id}'
            
            # Ensure username is unique
            while User.objects.filter(username=username).exists():
                unique_id = self.generate_random_string()
                username = f'divecenter_{unique_id}'
            
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='password123',
                first_name=f'Dive Center {unique_id.upper()}',
                last_name='Management'
            )
            
            user.userprofile.is_diving_center = True
            user.userprofile.business_name = f'Dive Center {unique_id.upper()} Ltd'
            user.userprofile.business_license = f'DC{unique_id.upper()}-2024'
            user.userprofile.location = random.choice(locations)
            user.userprofile.save()
            
            centers.append(user)
            self.stdout.write(f'Created diving center: {username}')
        
        return centers

    def create_customers(self, diving_centers, customers_per_center):
        customers = []
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa', 
            'Robert', 'Maria', 'James', 'Anna', 'Daniel', 'Sophie', 'Mark', 'Laura',
            'Peter', 'Julia', 'Thomas', 'Elena', 'Andrew', 'Kate', 'Ryan', 'Nicole',
            'Kevin', 'Amy', 'Brian', 'Rachel', 'Steven', 'Jessica', 'Matthew', 'Ashley',
            'William', 'Amanda', 'Richard', 'Jennifer', 'Joseph', 'Michelle', 'Charles', 'Kimberly'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King'
        ]
        
        countries = [choice[0] for choice in Customer.COUNTRY_CHOICES]
        languages = [choice[0] for choice in Customer.LANGUAGE_CHOICES]
        cert_levels = [choice[0] for choice in Customer.DIVING_LEVEL_CHOICES]
        tank_sizes = [choice[0] for choice in Customer._meta.get_field('default_tank_size').choices]
        
        for center in diving_centers:
            for i in range(customers_per_center):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                unique_id = self.generate_random_string(4)
                
                customer = Customer.objects.create(
                    diving_center=center,
                    first_name=first_name,
                    last_name=last_name,
                    email=f'{first_name.lower()}.{last_name.lower()}.{unique_id}@email.com',
                    phone_number=f'+{random.randint(1, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    country=random.choice(countries),
                    language=random.choice(languages),
                    birthday=date(
                        random.randint(1970, 2005),
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ),
                    certification_level=random.choice(cert_levels),
                    emergency_contact=f'Emergency Contact {unique_id}',
                    medical_conditions=random.choice([
                        '', 'None', 'Mild asthma', 'Allergic to seafood', 
                        'Previous knee surgery', 'Controlled diabetes', 'Heart condition',
                        'Back problems', 'Ear issues', 'Medication for blood pressure'
                    ]),
                    weight=round(random.uniform(50, 100), 1),
                    height=round(random.uniform(150, 195), 1),
                    foot_size=round(random.uniform(35, 46), 1),
                    default_tank_size=random.choice(tank_sizes)
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
            ('Drift Dive', 'Current diving experience', 60, 60.00),
            ('Cave Dive', 'Cave diving exploration', 120, 85.00),
            ('Photography Dive', 'Underwater photography session', 90, 65.00)
        ]
        
        for center in diving_centers:
            for name, desc, duration, base_price in activity_types:
                # Add some price variation
                price = base_price + random.uniform(-10, 15)
                
                activity = DiveActivity.objects.create(
                    diving_center=center,
                    name=name,
                    description=desc,
                    duration_minutes=duration + random.randint(-15, 30),
                    price=round(price, 2)
                )
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
            ('Manta Station', 'Manta ray cleaning station', 10, 25, 'BEGINNER'),
            ('Thunder Rock', 'Rocky underwater formation', 15, 35, 'ADVANCED'),
            ('Crystal Waters', 'Clear water diving spot', 5, 15, 'BEGINNER')
        ]
        
        for center in diving_centers:
            for name, desc, min_depth, max_depth, difficulty in site_data:
                unique_id = self.generate_random_string(3)
                site_name = f'{name} {unique_id.upper()}'
                
                site = DivingSite.objects.create(
                    diving_center=center,
                    name=site_name,
                    location=f'{site_name} Location - {center.userprofile.location}',
                    depth_min=min_depth + random.randint(-3, 5),
                    depth_max=max_depth + random.randint(-5, 10),
                    difficulty_level=difficulty,
                    description=desc + f' (Site {unique_id.upper()})',
                    special_requirements=random.choice([
                        '', 'Advanced certification required', 'Good buoyancy control needed',
                        'Strong swimming skills required', 'Previous deep diving experience',
                        'Nitrox certification recommended', 'Dry suit experience helpful'
                    ])
                )
                sites.append(site)
        
        self.stdout.write(f'Created {len(sites)} diving sites')
        return sites

    def create_dive_schedules(self, diving_centers, sites, activities, schedules_per_center):
        schedules = []
        start_date = date.today()
        
        for center in diving_centers:
            center_sites = [site for site in sites if site.diving_center == center]
            
            for i in range(schedules_per_center):
                dive_date = start_date + timedelta(days=random.randint(-30, 60))
                dive_time = time(
                    random.choice([7, 8, 9, 10, 11, 14, 15, 16, 17]),
                    random.choice([0, 30])
                )
                
                unique_id = self.generate_random_string(4)
                
                schedule = DiveSchedule.objects.create(
                    diving_center=center,
                    date=dive_date,
                    time=dive_time,
                    dive_site=random.choice(center_sites),
                    max_participants=random.randint(6, 20),
                    description=f'Scheduled dive {unique_id.upper()}',
                    special_notes=random.choice([
                        '', 'Bring underwater camera', 'Check weather conditions',
                        'Early arrival required', 'Equipment check mandatory',
                        'Nitrox fills available', 'Strong currents expected',
                        'Perfect for beginners', 'Advanced divers only'
                    ])
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
            num_participants = random.randint(2, min(8, schedule.max_participants))
            center_customers = [c for c in customers if c.diving_center == schedule.diving_center]
            
            if len(center_customers) >= num_participants:
                selected_customers = random.sample(center_customers, num_participants)
                center_activities = [a for a in activities if a.diving_center == schedule.diving_center]
                
                for customer in selected_customers:
                    # Check if customer is already in this dive
                    if not CustomerDiveActivity.objects.filter(
                        customer=customer,
                        dive_schedule=schedule
                    ).exists():
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
            ('3mm Wetsuit', 'WETSUIT', 'S', 6, 5),
            ('3mm Wetsuit', 'WETSUIT', 'M', 8, 7),
            ('3mm Wetsuit', 'WETSUIT', 'L', 6, 5),
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
            for name, category, size, base_total, base_available in inventory_data:
                # Add some variation to quantities
                total = base_total + random.randint(-2, 5)
                available = min(total, base_available + random.randint(-2, 3))
                
                unique_id = self.generate_random_string(3)
                
                item = InventoryItem.objects.create(
                    diving_center=center,
                    name=f'{name} {unique_id.upper()}',
                    category=category,
                    size=size,
                    quantity_total=max(1, total),
                    quantity_available=max(0, available),
                    condition=random.choice(conditions),
                    purchase_date=date.today() - timedelta(days=random.randint(30, 1000)),
                    last_maintenance=date.today() - timedelta(days=random.randint(1, 90)) if random.choice([True, False]) else None,
                    notes=random.choice(['', 'Needs maintenance soon', 'Recently serviced', 'Good condition', 'Check before use'])
                )
                items.append(item)
        
        self.stdout.write(f'Created {len(items)} inventory items')
        return items

    def create_diving_groups(self, diving_centers, groups_per_center):
        groups = []
        group_names = [
            'Ocean Explorers', 'Deep Blue Divers', 'Coral Seekers', 'Marine Adventurers',
            'Aqua Nomads', 'Blue Planet Team', 'Sea Wanderers', 'Dive Masters Club',
            'Underwater Photographers', 'Reef Guardians', 'Depth Hunters', 'Current Riders',
            'Blue Water Society', 'Marine Life Enthusiasts', 'Wreck Explorers', 'Bubble Makers',
            'Aquatic Adventures', 'Deep Sea Explorers', 'Ocean Warriors', 'Dive Squad'
        ]
        
        countries = [choice[0] for choice in Customer.COUNTRY_CHOICES]
        
        for center in diving_centers:
            for i in range(groups_per_center):
                group_name = random.choice(group_names)
                unique_id = self.generate_random_string(4)
                full_name = f'{group_name} {unique_id.upper()}'
                
                group = DivingGroup.objects.create(
                    diving_center=center,
                    name=full_name,
                    country=random.choice(countries),
                    contact_person=f'Contact Person {unique_id.upper()}',
                    email=f'group{unique_id}@{group_name.lower().replace(" ", "")}.com',
                    phone=f'+{random.randint(1, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    description=f'A group of diving enthusiasts from {group_name} (Group {unique_id.upper()})',
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
            
            if len(center_customers) >= num_members:
                selected_customers = random.sample(center_customers, num_members)
                
                for i, customer in enumerate(selected_customers):
                    # Check if customer is already in this group
                    if not DivingGroupMember.objects.filter(
                        group=group,
                        customer=customer
                    ).exists():
                        membership = DivingGroupMember.objects.create(
                            group=group,
                            customer=customer,
                            is_leader=(i == 0)  # First member is the leader
                        )
                        memberships.append(membership)
        
        self.stdout.write(f'Created {len(memberships)} group memberships')
        return memberships
