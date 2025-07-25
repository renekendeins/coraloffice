
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a superuser with predefined credentials'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='1111'
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created superuser "admin"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser "admin" already exists')
            )
