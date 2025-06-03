
# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_add_primary_instructor_to_enrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesession',
            name='template_course',
            field=models.ForeignKey(blank=True, help_text='Course this session template belongs to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='template_sessions', to='users.course'),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='enrollment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_sessions', to='users.courseenrollment'),
        ),
    ]
