
import random
import string
from datetime import date, time, datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from users.models import (
    UserProfile, Customer, DiveActivity, DivingSite, DiveSchedule, 
    CustomerDiveActivity, InventoryItem, DivingGroup, DivingGroupMember,
    Staff, Course, CourseEnrollment, CourseSession
)

class Command(BaseCommand):
    help = 'Populate database with realistic data for CIPS and MATEUA diving centers'

    def handle(self, *args, **options):
        self.stdout.write('Starting realistic database population...')
        
        try:
            with transaction.atomic():
                # Create diving centers
                diving_centers = self.create_diving_centers()
                
                # Create staff for each center
                staff_members = self.create_staff(diving_centers)
                
                # Create courses for each center
                courses = self.create_courses(diving_centers)
                
                # Create customers
                customers = self.create_customers(diving_centers)
                
                # Create diving sites
                sites = self.create_diving_sites(diving_centers)
                
                # Create dive schedules (past 3 months + next 3 months)
                schedules = self.create_dive_schedules(diving_centers, sites)
                
                # Create course enrollments with realistic progression
                enrollments = self.create_course_enrollments(customers, courses, staff_members)
                
                # Create course sessions and schedule them
                self.create_course_sessions(enrollments, schedules)
                
                # Create customer dive activities
                self.create_customer_dive_activities(customers, schedules, courses, staff_members)
                
                # Create inventory items
                self.create_inventory_items(diving_centers)
                
                # Create diving groups
                groups = self.create_diving_groups(diving_centers)
                
                # Create group members
                self.create_group_members(groups, customers)
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully populated database with realistic data!')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error populating database: {str(e)}')
            )

    def generate_random_string(self, length=8):
        """Generate random string for unique identifiers"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def create_diving_centers(self):
        centers_data = [
            ('cips', 'CIPS Diving Center', 'Mallorca, Spain'),
            ('mateua', 'MATEUA Diving Center', 'Costa Brava, Spain')
        ]
        
        centers = []
        for username, business_name, location in centers_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@diving.com',
                    'first_name': business_name.split()[0],
                    'last_name': 'Diving Center'
                }
            )
            
            if created:
                user.set_password('Password123')
                user.save()
            
            profile = user.userprofile
            profile.is_diving_center = True
            profile.business_name = business_name
            profile.business_license = f'{username.upper()}-2024'
            profile.location = location
            profile.save()
            
            centers.append(user)
            self.stdout.write(f'Created/Updated diving center: {username}')
        
        return centers

    def create_staff(self, diving_centers):
        staff_data = [
            ('Carlos', 'Martinez', 'INSTRUCTOR', 'Spanish, English', 8),
            ('Maria', 'Rodriguez', 'DIVEMASTER', 'Spanish, French', 5),
            ('James', 'Wilson', 'INSTRUCTOR', 'English, German', 12),
            ('Ana', 'Garcia', 'SENIOR_INSTRUCTOR', 'Spanish, Catalan', 15),
            ('Pierre', 'Dubois', 'DIVEMASTER', 'French, English', 3),
            ('Sofia', 'Rossi', 'INSTRUCTOR', 'Italian, English', 7),
            ('Miguel', 'Santos', 'CAPTAIN', 'Spanish, Portuguese', 20),
            ('Elena', 'Petrov', 'OFFICE', 'Russian, English', 2)
        ]
        
        all_staff = []
        for center in diving_centers:
            center_staff = []
            # Create 5-6 staff members per center
            staff_subset = random.sample(staff_data, random.randint(5, 6))
            
            for first_name, last_name, cert_level, languages, experience in staff_subset:
                unique_id = self.generate_random_string(3)
                email = f'{first_name.lower()}.{last_name.lower()}.{unique_id}@{center.username}.com'
                
                staff = Staff.objects.create(
                    diving_center=center,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=f'+34-{random.randint(600, 699)}-{random.randint(100000, 999999)}',
                    certification_level=cert_level,
                    certification_number=f'{cert_level}-{unique_id.upper()}',
                    languages=languages,
                    experience_years=experience,
                    hire_date=date.today() - timedelta(days=random.randint(30, 1000)),
                    hourly_rate=random.uniform(15.0, 45.0)
                )
                center_staff.append(staff)
                all_staff.append(staff)
            
            self.stdout.write(f'Created {len(center_staff)} staff members for {center.username}')
        
        return all_staff

    def create_courses(self, diving_centers):
        course_data = [
            ('Bautizo de Buceo', 'TRY_DIVE', 'Primera experiencia bajo el agua', 1, 1, 45.00),
            ('Inmersión Simple', 'SINGLE_DIVE', 'Inmersión recreativa individual', 1, 1, 35.00),
            ('Inmersión Doble', 'DOUBLE_DIVE', 'Dos inmersiones en el mismo día', 2, 1, 65.00),
            ('Curso Open Water', 'OPEN_WATER', 'Certificación PADI Open Water Diver', 4, 3, 350.00),
            ('Curso Advanced', 'ADVANCED_OPEN_WATER', 'Certificación PADI Advanced Open Water', 5, 2, 280.00),
            ('Especialidad Nitrox', 'NITROX', 'Certificación en aire enriquecido', 2, 1, 120.00),
            ('Buceo Nocturno', 'NIGHT', 'Especialidad en buceo nocturno', 3, 2, 150.00),
            ('Buceo Profundo', 'DEEP', 'Especialidad en buceo profundo', 4, 2, 180.00),
            ('Curso de Refresco', 'REFRESH', 'Reactivación de habilidades', 2, 1, 80.00),
            ('Fotografía Submarina', 'PHOTOGRAPHY', 'Especialidad en fotografía', 3, 2, 200.00)
        ]
        
        all_courses = []
        for center in diving_centers:
            center_courses = []
            
            for name, course_type, description, total_dives, duration_days, base_price in course_data:
                # Add some price variation between centers
                price = base_price + random.uniform(-10, 20)
                
                course = Course.objects.create(
                    diving_center=center,
                    name=name,
                    course_type=course_type,
                    description=description,
                    total_dives=total_dives,
                    duration_days=duration_days,
                    price=round(price, 2),
                    just_one_dive=(total_dives == 1),
                    includes_material=random.choice([True, True, True, False]),  # Mostly true
                    includes_instructor=True,
                    includes_insurance=random.choice([True, True, False])  # Mostly true
                )
                center_courses.append(course)
                all_courses.append(course)
            
            self.stdout.write(f'Created {len(center_courses)} courses for {center.username}')
        
        return all_courses

    def create_customers(self, diving_centers):
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa', 
            'Robert', 'Maria', 'James', 'Anna', 'Daniel', 'Sophie', 'Mark', 'Laura',
            'Peter', 'Julia', 'Thomas', 'Elena', 'Andrew', 'Kate', 'Ryan', 'Nicole',
            'Kevin', 'Amy', 'Brian', 'Rachel', 'Steven', 'Jessica', 'Matthew', 'Ashley',
            'William', 'Amanda', 'Richard', 'Jennifer', 'Joseph', 'Michelle', 'Charles', 'Kimberly',
            'Pablo', 'Carmen', 'Alejandro', 'Isabella', 'Diego', 'Valentina', 'Carlos', 'Camila',
            'Antonio', 'Lucia', 'Francisco', 'Martina', 'Manuel', 'Valeria', 'Javier', 'Natalia'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
            'Fernandez', 'Morales', 'Jimenez', 'Ruiz', 'Navarro', 'Castillo', 'Torres'
        ]
        
        countries = [choice[0] for choice in Customer.COUNTRY_CHOICES]
        languages = [choice[0] for choice in Customer.LANGUAGE_CHOICES]
        cert_levels = [choice[0] for choice in Customer.DIVING_LEVEL_CHOICES]
        tank_sizes = [choice[0] for choice in Customer._meta.get_field('default_tank_size').choices]
        
        all_customers = []
        for center in diving_centers:
            center_customers = []
            # Create 30-40 customers per center
            num_customers = random.randint(30, 40)
            
            for i in range(num_customers):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                unique_id = self.generate_random_string(4)
                
                # Create customers with varied registration dates (simulate app usage over time)
                created_date = date.today() - timedelta(days=random.randint(30, 365))
                
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
                
                # Set the created_at to simulate historical data
                customer.created_at = datetime.combine(created_date, datetime.min.time())
                customer.save()
                
                center_customers.append(customer)
                all_customers.append(customer)
            
            self.stdout.write(f'Created {len(center_customers)} customers for {center.username}')
        
        return all_customers

    def create_diving_sites(self, diving_centers):
        sites_data = {
            'cips': [
                ('Es Vedranell', 'Iconic rocky formation', 8, 25, 'INTERMEDIATE'),
                ('Cathedral Cave', 'Underwater cave system', 12, 35, 'ADVANCED'),
                ('Coral Garden Mallorca', 'Beautiful coral formations', 5, 18, 'BEGINNER'),
                ('Blue Grotto', 'Spectacular blue water cave', 10, 28, 'INTERMEDIATE'),
                ('Wall of Mirrors', 'Vertical wall dive', 15, 40, 'ADVANCED'),
                ('Turtle Bay', 'Sea turtle sanctuary', 6, 20, 'BEGINNER'),
                ('Wreck of Santa Eulalia', 'Historic shipwreck', 18, 35, 'ADVANCED'),
                ('Posidonia Meadows', 'Seagrass ecosystem', 8, 22, 'BEGINNER')
            ],
            'mateua': [
                ('Medes Islands', 'Protected marine reserve', 10, 30, 'INTERMEDIATE'),
                ('Dolphin Point', 'Dolphin observation site', 12, 25, 'INTERMEDIATE'),
                ('Costa Brava Reef', 'Vibrant reef system', 6, 20, 'BEGINNER'),
                ('Deep Canyon', 'Underwater canyon', 20, 45, 'EXPERT'),
                ('Octopus Garden', 'Octopus habitat', 8, 24, 'BEGINNER'),
                ('Current Ride', 'Drift diving site', 15, 35, 'ADVANCED'),
                ('Night Dive Special', 'Perfect for night diving', 10, 28, 'INTERMEDIATE'),
                ('Barracuda Point', 'Barracuda aggregation site', 14, 32, 'INTERMEDIATE')
            ]
        }
        
        all_sites = []
        for center in diving_centers:
            center_sites = []
            center_site_data = sites_data.get(center.username, sites_data['cips'])
            
            for name, desc, min_depth, max_depth, difficulty in center_site_data:
                site = DivingSite.objects.create(
                    diving_center=center,
                    name=name,
                    location=f'{name} - {center.userprofile.location}',
                    depth_min=min_depth + random.randint(-2, 3),
                    depth_max=max_depth + random.randint(-3, 5),
                    difficulty_level=difficulty,
                    description=desc,
                    special_requirements=random.choice([
                        '', 'Advanced certification required', 'Good buoyancy control needed',
                        'Strong swimming skills required', 'Previous deep diving experience',
                        'Nitrox certification recommended', 'Dry suit experience helpful'
                    ])
                )
                center_sites.append(site)
                all_sites.append(site)
            
            self.stdout.write(f'Created {len(center_sites)} diving sites for {center.username}')
        
        return all_sites

    def create_dive_schedules(self, diving_centers, sites):
        all_schedules = []
        
        # Create schedules for past 3 months and next 3 months
        start_date = date.today() - timedelta(days=90)
        end_date = date.today() + timedelta(days=90)
        
        for center in diving_centers:
            center_sites = [site for site in sites if site.diving_center == center]
            center_schedules = []
            
            current_date = start_date
            while current_date <= end_date:
                # Skip some days randomly to simulate realistic scheduling
                if random.random() < 0.3:  # 30% chance to skip a day
                    current_date += timedelta(days=1)
                    continue
                
                # Create 2-4 dive schedules per active day
                num_dives = random.randint(2, 4)
                
                for i in range(num_dives):
                    dive_time = time(
                        random.choice([8, 9, 10, 11, 14, 15, 16, 17]),
                        random.choice([0, 30])
                    )
                    
                    schedule = DiveSchedule.objects.create(
                        diving_center=center,
                        date=current_date,
                        time=dive_time,
                        dive_site=random.choice(center_sites),
                        max_participants=random.randint(8, 16),
                        description=f'Dive at {random.choice(center_sites).name}',
                        special_notes=random.choice([
                            '', 'Bring underwater camera', 'Check weather conditions',
                            'Early arrival required', 'Equipment check mandatory',
                            'Nitrox fills available', 'Strong currents expected',
                            'Perfect visibility expected', 'Marine life spotting likely'
                        ])
                    )
                    center_schedules.append(schedule)
                    all_schedules.append(schedule)
                
                current_date += timedelta(days=1)
            
            self.stdout.write(f'Created {len(center_schedules)} dive schedules for {center.username}')
        
        return all_schedules

    def create_course_enrollments(self, customers, courses, staff_members):
        all_enrollments = []
        
        for customer in customers:
            # Each customer has 1-3 course enrollments with realistic distribution
            num_enrollments = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            
            center_courses = [c for c in courses if c.diving_center == customer.diving_center]
            center_staff = [s for s in staff_members if s.diving_center == customer.diving_center and s.certification_level in ['INSTRUCTOR', 'SENIOR_INSTRUCTOR', 'MASTER_INSTRUCTOR']]
            
            if len(center_courses) >= num_enrollments:
                selected_courses = random.sample(center_courses, num_enrollments)
                
                for course in selected_courses:
                    # Create enrollment with realistic dates (some in the past, some ongoing, some future)
                    enrollment_date = date.today() - timedelta(days=random.randint(1, 180))
                    
                    # Determine status based on enrollment date and course duration
                    days_since_enrollment = (date.today() - enrollment_date).days
                    
                    if days_since_enrollment > course.duration_days + 30:
                        status = 'COMPLETED'
                        completion_date = enrollment_date + timedelta(days=course.duration_days + random.randint(0, 10))
                        start_date = enrollment_date + timedelta(days=random.randint(1, 7))
                    elif days_since_enrollment > course.duration_days:
                        status = random.choice(['COMPLETED', 'IN_PROGRESS'])
                        completion_date = enrollment_date + timedelta(days=course.duration_days + random.randint(0, 10)) if status == 'COMPLETED' else None
                        start_date = enrollment_date + timedelta(days=random.randint(1, 7))
                    elif days_since_enrollment > 7:
                        status = 'IN_PROGRESS'
                        completion_date = None
                        start_date = enrollment_date + timedelta(days=random.randint(1, 7))
                    else:
                        status = 'ENROLLED'
                        completion_date = None
                        start_date = None
                    
                    enrollment = CourseEnrollment.objects.create(
                        customer=customer,
                        course=course,
                        primary_instructor=random.choice(center_staff) if center_staff else None,
                        status=status,
                        enrollment_date=enrollment_date,
                        start_date=start_date,
                        completion_date=completion_date,
                        is_paid=random.choice([True, True, True, False]),  # Mostly paid
                        price_paid=course.price if random.choice([True, False]) else course.price * 0.9  # Some discounts
                    )
                    all_enrollments.append(enrollment)
        
        self.stdout.write(f'Created {len(all_enrollments)} course enrollments')
        return all_enrollments

    def create_course_sessions(self, enrollments, schedules):
        all_sessions = []
        
        for enrollment in enrollments:
            # Create sessions for each enrollment based on course structure
            for session_num in range(1, enrollment.course.total_dives + 1):
                session_title = f"Session {session_num}"
                if enrollment.course.course_type == 'OPEN_WATER':
                    titles = ['Pool Skills', 'Open Water Dive 1', 'Open Water Dive 2', 'Final Skills Assessment']
                    session_title = titles[min(session_num - 1, len(titles) - 1)]
                elif enrollment.course.course_type == 'ADVANCED_OPEN_WATER':
                    titles = ['Deep Dive', 'Navigation Dive', 'Night Dive', 'Wreck Dive', 'Final Assessment']
                    session_title = titles[min(session_num - 1, len(titles) - 1)]
                elif enrollment.course.course_type == 'TRY_DIVE':
                    session_title = 'Discover Scuba'
                elif enrollment.course.course_type in ['SINGLE_DIVE', 'DOUBLE_DIVE']:
                    session_title = f'Recreational Dive {session_num}'
                
                # Determine session status and scheduling based on enrollment status
                if enrollment.status == 'COMPLETED':
                    session_status = 'COMPLETED'
                    # Schedule in the past
                    session_date = enrollment.start_date + timedelta(days=(session_num - 1) * 2)
                    completion_date = datetime.combine(session_date, time(12, 0))
                elif enrollment.status == 'IN_PROGRESS':
                    if session_num <= enrollment.course.total_dives // 2:
                        session_status = 'COMPLETED'
                        session_date = enrollment.start_date + timedelta(days=(session_num - 1) * 2)
                        completion_date = datetime.combine(session_date, time(12, 0))
                    else:
                        session_status = random.choice(['SCHEDULED', 'NOT_SCHEDULED'])
                        if session_status == 'SCHEDULED':
                            session_date = date.today() + timedelta(days=random.randint(1, 14))
                        else:
                            session_date = None
                        completion_date = None
                else:  # ENROLLED
                    session_status = 'NOT_SCHEDULED'
                    session_date = None
                    completion_date = None
                
                # Find a suitable dive schedule if session is scheduled
                dive_schedule = None
                if session_status in ['SCHEDULED', 'COMPLETED'] and session_date:
                    # Find schedules for the same diving center on the same date
                    suitable_schedules = [
                        s for s in schedules 
                        if s.diving_center == enrollment.course.diving_center 
                        and s.date == session_date
                    ]
                    if suitable_schedules:
                        dive_schedule = random.choice(suitable_schedules)
                
                session = CourseSession.objects.create(
                    enrollment=enrollment,
                    session_number=session_num,
                    title=session_title,
                    description=f"{session_title} for {enrollment.course.name}",
                    status=session_status,
                    dive_schedule=dive_schedule,
                    instructor=enrollment.primary_instructor,
                    scheduled_date=session_date,
                    scheduled_time=dive_schedule.time if dive_schedule else None,
                    completion_date=completion_date,
                    grade=random.choice(['Passed', 'Excellent', 'Good']) if session_status == 'COMPLETED' else ''
                )
                all_sessions.append(session)
        
        self.stdout.write(f'Created {len(all_sessions)} course sessions')
        return all_sessions

    def create_customer_dive_activities(self, customers, schedules, courses, staff_members):
        all_activities = []
        tank_sizes = [choice[0] for choice in CustomerDiveActivity.TANK_SIZE_CHOICES]
        statuses = [choice[0] for choice in CustomerDiveActivity.STATUS_CHOICES]
        
        for schedule in schedules:
            # Add 3-8 participants per dive
            num_participants = random.randint(3, min(8, schedule.max_participants))
            center_customers = [c for c in customers if c.diving_center == schedule.diving_center]
            center_courses = [c for c in courses if c.diving_center == schedule.diving_center and c.just_one_dive]
            center_staff = [s for s in staff_members if s.diving_center == schedule.diving_center]
            
            if len(center_customers) >= num_participants:
                selected_customers = random.sample(center_customers, num_participants)
                
                for customer in selected_customers:
                    # Check if customer is already in this dive
                    if not CustomerDiveActivity.objects.filter(
                        customer=customer,
                        dive_schedule=schedule
                    ).exists():
                        
                        # Select appropriate course (prefer single dive activities for regular dives)
                        course = random.choice(center_courses) if center_courses else None
                        
                        # Determine status based on dive date
                        if schedule.date < date.today():
                            activity_status = random.choice(['FINISHED', 'FINISHED', 'FINISHED', 'DEPARTED'])
                        elif schedule.date == date.today():
                            activity_status = random.choice(['ON_BOARD', 'BACK_ON_BOAT', 'DEPARTED'])
                        else:
                            activity_status = 'PENDING'
                        
                        activity = CustomerDiveActivity.objects.create(
                            customer=customer,
                            dive_schedule=schedule,
                            course=course,
                            assigned_staff=random.choice(center_staff) if center_staff else None,
                            tank_size=random.choice(tank_sizes),
                            needs_wetsuit=random.choice([True, False]),
                            needs_bcd=random.choice([True, False]),
                            needs_regulator=random.choice([True, False]),
                            needs_fins=random.choice([True, False]),
                            needs_guide=random.choice([True, False]),
                            needs_insurance=random.choice([True, False]),
                            status=activity_status,
                            has_arrived=(activity_status != 'PENDING'),
                            is_paid=random.choice([True, True, True, False])  # Mostly paid
                        )
                        all_activities.append(activity)
        
        self.stdout.write(f'Created {len(all_activities)} customer dive activities')
        return all_activities

    def create_inventory_items(self, diving_centers):
        inventory_data = [
            ('5mm Wetsuit', 'WETSUIT', 'XS', 3, 3),
            ('5mm Wetsuit', 'WETSUIT', 'S', 6, 5),
            ('5mm Wetsuit', 'WETSUIT', 'M', 10, 8),
            ('5mm Wetsuit', 'WETSUIT', 'L', 8, 6),
            ('5mm Wetsuit', 'WETSUIT', 'XL', 4, 3),
            ('3mm Wetsuit', 'WETSUIT', 'S', 4, 4),
            ('3mm Wetsuit', 'WETSUIT', 'M', 6, 5),
            ('3mm Wetsuit', 'WETSUIT', 'L', 4, 3),
            ('BCD Vest', 'BCD', 'S', 5, 5),
            ('BCD Vest', 'BCD', 'M', 8, 7),
            ('BCD Vest', 'BCD', 'L', 6, 5),
            ('BCD Vest', 'BCD', 'XL', 3, 3),
            ('Regulator Set', 'REGULATOR', 'N/A', 12, 10),
            ('Fins', 'FINS', 'S', 6, 5),
            ('Fins', 'FINS', 'M', 10, 8),
            ('Fins', 'FINS', 'L', 8, 6),
            ('Diving Mask', 'MASK', 'N/A', 15, 12),
            ('Diving Boots', 'BOOTS', 'S', 4, 3),
            ('Diving Boots', 'BOOTS', 'M', 6, 5),
            ('Diving Boots', 'BOOTS', 'L', 4, 3),
            ('12L Tank', 'TANK', 'N/A', 15, 12),
            ('15L Tank', 'TANK', 'N/A', 8, 6),
            ('Weight Belt', 'WEIGHT', 'N/A', 10, 8)
        ]
        
        conditions = ['EXCELLENT', 'GOOD', 'FAIR', 'POOR']
        
        all_items = []
        for center in diving_centers:
            center_items = []
            
            for name, category, size, base_total, base_available in inventory_data:
                # Add some variation to quantities
                total = base_total + random.randint(-1, 3)
                available = min(total, base_available + random.randint(-1, 2))
                
                item = InventoryItem.objects.create(
                    diving_center=center,
                    name=name,
                    category=category,
                    size=size,
                    quantity_total=max(1, total),
                    quantity_available=max(0, available),
                    condition=random.choice(conditions),
                    purchase_date=date.today() - timedelta(days=random.randint(30, 800)),
                    last_maintenance=date.today() - timedelta(days=random.randint(1, 60)) if random.choice([True, False]) else None,
                    notes=random.choice([
                        '', 'Needs maintenance soon', 'Recently serviced', 
                        'Good condition', 'Check before use', 'New equipment'
                    ])
                )
                center_items.append(item)
                all_items.append(item)
            
            self.stdout.write(f'Created {len(center_items)} inventory items for {center.username}')
        
        return all_items

    def create_diving_groups(self, diving_centers):
        group_names = [
            'Ocean Explorers', 'Deep Blue Divers', 'Coral Seekers', 'Marine Adventurers',
            'Aqua Nomads', 'Blue Planet Team', 'Sea Wanderers', 'Dive Masters Club',
            'Underwater Photographers', 'Reef Guardians', 'Depth Hunters', 'Current Riders',
            'Blue Water Society', 'Marine Life Enthusiasts', 'Wreck Explorers', 'Bubble Makers',
            'Aquatic Adventures', 'Deep Sea Explorers', 'Ocean Warriors', 'Dive Squad'
        ]
        
        countries = [choice[0] for choice in Customer.COUNTRY_CHOICES]
        
        all_groups = []
        for center in diving_centers:
            center_groups = []
            # Create 8-12 groups per center
            num_groups = random.randint(8, 12)
            
            for i in range(num_groups):
                group_name = random.choice(group_names)
                unique_id = self.generate_random_string(4)
                full_name = f'{group_name} {unique_id.upper()}'
                
                # Create groups arriving in different periods
                arrival_date = date.today() + timedelta(days=random.randint(-30, 60))
                departure_date = arrival_date + timedelta(days=random.randint(3, 14))
                
                group = DivingGroup.objects.create(
                    diving_center=center,
                    name=full_name,
                    country=random.choice(countries),
                    contact_person=f'Contact Person {unique_id.upper()}',
                    email=f'group{unique_id}@{group_name.lower().replace(" ", "")}.com',
                    phone=f'+{random.randint(1, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    description=f'A group of diving enthusiasts from {group_name} (Group {unique_id.upper()})',
                    arrival_date=arrival_date,
                    departure_date=departure_date
                )
                center_groups.append(group)
                all_groups.append(group)
            
            self.stdout.write(f'Created {len(center_groups)} diving groups for {center.username}')
        
        return all_groups

    def create_group_members(self, groups, customers):
        all_memberships = []
        
        for group in groups:
            # Each group has 4-8 members
            num_members = random.randint(4, 8)
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
                        all_memberships.append(membership)
        
        self.stdout.write(f'Created {len(all_memberships)} group memberships')
        return all_memberships
