
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
    help = 'Populate database with sample data for divecenter1 user'

    def handle(self, *args, **options):
        self.stdout.write('Starting database population for divecenter1...')
        
        try:
            # Get divecenter1 user
            try:
                diving_center = User.objects.get(username='divingcenter1')
                if not diving_center.userprofile.is_diving_center:
                    self.stdout.write(
                        self.style.ERROR('divecenter1 user is not configured as a diving center')
                    )
                    return
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('divecenter1 user does not exist. Please create it first.')
                )
                return

            with transaction.atomic():
                # Create customers
                customers = self.create_customers(diving_center)
                
                # Create diving activities
                activities = self.create_activities(diving_center)
                
                # Create diving sites
                sites = self.create_diving_sites(diving_center)
                
                # Create dive schedules
                schedules = self.create_dive_schedules(diving_center, sites, activities)
                
                # Create customer dive activities
                self.create_customer_dive_activities(customers, schedules, activities)
                
                # Create inventory items
                self.create_inventory_items(diving_center)
                
                # Create diving groups
                groups = self.create_diving_groups(diving_center)
                
                # Create group members
                self.create_group_members(groups, customers)
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully populated database for divecenter1!')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error populating database: {str(e)}')
            )

    def generate_random_string(self, length=8):
        """Generate random string for unique identifiers"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def create_customers(self, diving_center):
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
        
        for i in range(25):  # Create 25 customers for divecenter1
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            unique_id = self.generate_random_string(4)
            
            customer = Customer.objects.create(
                diving_center=diving_center,
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
                default_tank_size=random.choice(tank_sizes),
                diving_insurance=random.choice([True, False]),
                diving_licence=random.choice([True, False]),
                medical_check=random.choice([True, False])
            )
            customers.append(customer)
        
        self.stdout.write(f'Created {len(customers)} customers for divecenter1')
        return customers

    def create_activities(self, diving_center):
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
        
        for name, desc, duration, base_price in activity_types:
            # Add some price variation
            price = base_price + random.uniform(-10, 15)
            
            activity, created = DiveActivity.objects.get_or_create(
                diving_center=diving_center,
                name=name,
                defaults={
                    'description': desc,
                    'duration_minutes': duration + random.randint(-15, 30),
                    'price': round(price, 2)
                }
            )
            if created:
                activities.append(activity)
        
        self.stdout.write(f'Created {len(activities)} activities for divecenter1')
        return activities

    def create_diving_sites(self, diving_center):
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
        
        for name, desc, min_depth, max_depth, difficulty in site_data:
            site, created = DivingSite.objects.get_or_create(
                diving_center=diving_center,
                name=name,
                defaults={
                    'location': f'{name} Location - Maldives',
                    'depth_min': min_depth + random.randint(-3, 5),
                    'depth_max': max_depth + random.randint(-5, 10),
                    'difficulty_level': difficulty,
                    'description': desc,
                    'special_requirements': random.choice([
                        '', 'Advanced certification required', 'Good buoyancy control needed',
                        'Strong swimming skills required', 'Previous deep diving experience',
                        'Nitrox certification recommended', 'Dry suit experience helpful'
                    ])
                }
            )
            if created:
                sites.append(site)
        
        self.stdout.write(f'Created {len(sites)} diving sites for divecenter1')
        return sites

    def create_dive_schedules(self, diving_center, sites, activities):
        schedules = []
        start_date = date.today()
        
        for i in range(20):  # Create 20 dive schedules
            dive_date = start_date + timedelta(days=random.randint(-15, 45))
            dive_time = time(
                random.choice([7, 8, 9, 10, 11, 14, 15, 16, 17]),
                random.choice([0, 30])
            )
            
            unique_id = self.generate_random_string(4)
            
            schedule = DiveSchedule.objects.create(
                diving_center=diving_center,
                date=dive_date,
                time=dive_time,
                dive_site=random.choice(sites),
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
        
        self.stdout.write(f'Created {len(schedules)} dive schedules for divecenter1')
        return schedules

    def create_customer_dive_activities(self, customers, schedules, activities):
        participations = []
        tank_sizes = [choice[0] for choice in CustomerDiveActivity.TANK_SIZE_CHOICES]
        statuses = [choice[0] for choice in CustomerDiveActivity.STATUS_CHOICES]
        
        for schedule in schedules:
            # Add 3-8 participants per dive
            num_participants = random.randint(3, min(8, schedule.max_participants))
            
            if len(customers) >= num_participants:
                selected_customers = random.sample(customers, num_participants)
                
                for customer in selected_customers:
                    # Check if customer is already in this dive
                    if not CustomerDiveActivity.objects.filter(
                        customer=customer,
                        dive_schedule=schedule
                    ).exists():
                        participation = CustomerDiveActivity.objects.create(
                            customer=customer,
                            dive_schedule=schedule,
                            activity=random.choice(activities),
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
        
        self.stdout.write(f'Created {len(participations)} customer dive activities for divecenter1')
        return participations

    def create_inventory_items(self, diving_center):
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
        
        for name, category, size, base_total, base_available in inventory_data:
            # Add some variation to quantities
            total = base_total + random.randint(-2, 5)
            available = min(total, base_available + random.randint(-2, 3))
            
            unique_id = self.generate_random_string(3)
            
            item = InventoryItem.objects.create(
                diving_center=diving_center,
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
        
        self.stdout.write(f'Created {len(items)} inventory items for divecenter1')
        return items

    def create_diving_groups(self, diving_center):
        groups = []
        group_names = [
            'Ocean Explorers', 'Deep Blue Divers', 'Coral Seekers', 'Marine Adventurers',
            'Aqua Nomads', 'Blue Planet Team', 'Sea Wanderers', 'Dive Masters Club',
            'Underwater Photographers', 'Reef Guardians'
        ]
        
        countries = [choice[0] for choice in Customer.COUNTRY_CHOICES]
        
        for i in range(10):  # Create 10 diving groups
            group_name = random.choice(group_names)
            unique_id = self.generate_random_string(4)
            full_name = f'{group_name} {unique_id.upper()}'
            
            group = DivingGroup.objects.create(
                diving_center=diving_center,
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
        
        self.stdout.write(f'Created {len(groups)} diving groups for divecenter1')
        return groups

    def create_group_members(self, groups, customers):
        memberships = []
        
        for group in groups:
            # Each group has 3-6 members
            num_members = random.randint(3, 6)
            
            if len(customers) >= num_members:
                selected_customers = random.sample(customers, num_members)
                
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
        
        self.stdout.write(f'Created {len(memberships)} group memberships for divecenter1')
        return memberships
