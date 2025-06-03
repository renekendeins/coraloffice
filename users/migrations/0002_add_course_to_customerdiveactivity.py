
# Generated migration file

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerdiveactivity',
            name='course',
            field=models.ForeignKey(help_text='Course/Activity for this dive', null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_bookings', to='users.course'),
        ),
        migrations.AlterField(
            model_name='customerdiveactivity',
            name='activity',
            field=models.ForeignKey(blank=True, help_text='DEPRECATED: Use course field instead', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_bookings', to='users.diveactivity'),
        ),
    ]
