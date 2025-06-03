
# Generated migration for adding JUST_ONE_DIVE course type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_course_course_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_type',
            field=models.CharField(choices=[('OPEN_WATER', 'Open Water Diver'), ('ADVANCED_OPEN_WATER', 'Advanced Open Water'), ('RESCUE_DIVER', 'Rescue Diver'), ('DIVEMASTER', 'Divemaster'), ('NITROX', 'Nitrox Specialty'), ('DEEP', 'Deep Diver Specialty'), ('WRECK', 'Wreck Diver Specialty'), ('NIGHT', 'Night Diver Specialty'), ('NAVIGATION', 'Underwater Navigation'), ('PHOTOGRAPHY', 'Underwater Photography'), ('SINGLE_DIVE', 'Inmersión Simple'), ('DOUBLE_DIVE', 'Inmersión Doble'), ('TRY_DIVE', 'Bautizo'), ('SCUBA_DIVER', 'Scuba Diver'), ('DIVING_LESSON', 'Clase de Buceo'), ('REFRESH', 'Refresh'), ('JUST_ONE_DIVE', 'Just One Dive'), ('CUSTOM', 'Custom Course')], default='CUSTOM', max_length=30),
        ),
    ]
