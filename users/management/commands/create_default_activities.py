import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import DiveActivity



# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')  # Cambia 'tu_proyecto'
django.setup()


class Command(BaseCommand):
    help = 'Creates default dive activities for all diving centers'

    def handle(self, *args, **options):
        default_activities = [
            {
                'name': 'Try Dive',
                'description': 'Introductory dive for beginners with no certification required',
                'duration_minutes': 60,
                'price': 45.00
            },
            {
                'name': 'Single Dive',
                'description': 'Single recreational dive for certified divers',
                'duration_minutes': 45,
                'price': 35.00
            },
            {
                'name': 'Double Dive',
                'description': 'Two dives in the same trip for certified divers',
                'duration_minutes': 120,
                'price': 65.00
            },
            {
                'name': 'Open Water Course',
                'description': 'PADI Open Water Diver certification course',
                'duration_minutes': 480,
                'price': 350.00
            },
            {
                'name': 'Advanced Open Water Course',
                'description': 'PADI Advanced Open Water Diver certification course',
                'duration_minutes': 360,
                'price': 280.00
            },
            {
                'name': 'Rescue Diver Course',
                'description': 'PADI Rescue Diver certification course',
                'duration_minutes': 600,
                'price': 450.00
            },
            {
                'name': 'Night Dive',
                'description': 'Guided night diving experience',
                'duration_minutes': 60,
                'price': 50.00
            },
            {
                'name': 'Deep Dive',
                'description': 'Deep water diving for advanced divers',
                'duration_minutes': 75,
                'price': 55.00
            }
        ]

        diving_centers = User.objects.filter(userprofile__is_diving_center=True)
        
        for center in diving_centers:
            for activity_data in default_activities:
                activity, created = DiveActivity.objects.get_or_create(
                    diving_center=center,
                    name=activity_data['name'],
                    defaults=activity_data
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created activity "{activity.name}" for {center.username}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Activity "{activity.name}" already exists for {center.username}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully processed default activities for all diving centers')
        )
