
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Display instructions for setting up email configuration'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Email Configuration Setup Instructions')
        )
        self.stdout.write('=' * 50)
        
        self.stdout.write('\n1. For Gmail (recommended for testing):')
        self.stdout.write('   - Enable 2-factor authentication on your Gmail account')
        self.stdout.write('   - Generate an App Password: https://myaccount.google.com/apppasswords')
        self.stdout.write('   - Set these environment variables in Replit Secrets:')
        self.stdout.write('     EMAIL_HOST_USER=your-email@gmail.com')
        self.stdout.write('     EMAIL_HOST_PASSWORD=your-app-password')
        self.stdout.write('     DEFAULT_FROM_EMAIL=your-email@gmail.com')
        
        self.stdout.write('\n2. For development testing (console output):')
        self.stdout.write('   - Uncomment the console backend line in settings.py')
        self.stdout.write('   - Emails will be printed to the console instead')
        
        self.stdout.write('\n3. Test your configuration:')
        self.stdout.write('   python manage.py send_test_email --email your-test@email.com')
        
        self.stdout.write('\n4. Available languages for emails:')
        self.stdout.write('   EN (English), ES (Spanish), FR (French), CAT (Catalan), DE (German)')
        
        self.stdout.write(
            self.style.WARNING('\nNote: Make sure to set up your email credentials in Replit Secrets before testing!')
        )
