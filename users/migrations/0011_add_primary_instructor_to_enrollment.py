
# Generated migration to add primary_instructor field to CourseEnrollment

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_coursesession_skills_covered'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='primary_instructor',
            field=models.ForeignKey(blank=True, help_text='Main instructor responsible for this course', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_course_enrollments', to='users.staff'),
        ),
    ]
