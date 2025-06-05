
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Customer, DiveSchedule, Course
from users.utils import send_dive_reminder_email, send_welcome_email
from datetime import date, time, timedelta


class Command(BaseCommand):
    help = 'Send test emails to verify email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test emails to',
            required=True
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['welcome', 'reminder', 'both'],
            default='both',
            help='Type of email to send (welcome, reminder, or both)'
        )
        parser.add_argument(
            '--language',
            type=str,
            choices=['EN', 'ES', 'FR', 'CAT', 'DE'],
            default='EN',
            help='Language for the email'
        )

    def handle(self, *args, **options):
        email = options['email']
        email_type = options['type']
        language = options['language']

        # Get or create a test diving center
        diving_center, created = User.objects.get_or_create(
            username='test_diving_center',
            defaults={
                'email': 'test@divingcenter.com',
                'first_name': 'Test',
                'last_name': 'Diving Center'
            }
        )

        if created:
            diving_center.userprofile.is_diving_center = True
            diving_center.userprofile.business_name = 'Test Diving Center'
            diving_center.userprofile.save()

        # Create a test customer
        test_customer = Customer.objects.create(
            diving_center=diving_center,
            first_name='Test',
            last_name='Customer',
            email=email,
            phone_number='+1234567890',
            language=language,
            country='ES'
        )

        if email_type in ['welcome', 'both']:
            self.stdout.write('Sending welcome email...')
            success = send_welcome_email(test_customer)
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Welcome email sent successfully to {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to send welcome email')
                )

        if email_type in ['reminder', 'both']:
            # Create test dive schedule and course for reminder email
            from users.models import DivingSite

            dive_site, created = DivingSite.objects.get_or_create(
                diving_center=diving_center,
                name='Test Dive Site',
                defaults={
                    'location': 'Test Location',
                    'depth_min': 5.0,
                    'depth_max': 30.0,
                    'difficulty_level': 'BEGINNER',
                    'description': 'A perfect site for testing emails'
                }
            )

            course, created = Course.objects.get_or_create(
                diving_center=diving_center,
                name='Open Water Diver Course',
                defaults={
                    'course_type': 'OPEN_WATER',
                    'description': 'Learn to dive safely',
                    'total_dives': 4,
                    'duration_days': 3,
                    'price': 350.00,
                    'includes_material': True,
                    'includes_instructor': True,
                    'includes_insurance': True
                }
            )

            dive_schedule = DiveSchedule.objects.create(
                diving_center=diving_center,
                date=date.today() + timedelta(days=1),
                time=time(10, 0),
                dive_site=dive_site,
                max_participants=12,
                description='Test dive for email verification',
                special_notes='Please bring your certification and towel'
            )

            self.stdout.write('Sending dive reminder email...')
            success = send_dive_reminder_email(test_customer, dive_schedule, course)
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Dive reminder email sent successfully to {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to send dive reminder email')
                )

        # Clean up test data
        test_customer.delete()
        if created:
            diving_center.delete()

        self.stdout.write(
            self.style.SUCCESS('Test email process completed!')
        )
