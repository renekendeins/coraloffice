
# Generated migration file

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_migrate_activities_to_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdiveactivity',
            name='course',
            field=models.ForeignKey(help_text='Course/Activity for this dive', on_delete=django.db.models.deletion.CASCADE, related_name='customer_bookings', to='users.course'),
        ),
    ]
