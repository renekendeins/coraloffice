
# Generated migration for adding default_tank_size field to Customer model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_diveschedule_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='default_tank_size',
            field=models.CharField(choices=[('10L', '10 Liters'), ('12L', '12 Liters'), ('15L', '15 Liters'), ('18L', '18 Liters')], default='12L', help_text='Default tank size for this customer', max_length=10),
        ),
    ]
