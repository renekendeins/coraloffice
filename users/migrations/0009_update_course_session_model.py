
# Generated migration for course session updates

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_course_courseenrollment_coursesession_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesession',
            name='assistant_instructors',
            field=models.ManyToManyField(blank=True, help_text='Additional staff members assisting this lesson', related_name='assisting_sessions', to='users.staff'),
        ),
        migrations.AddField(
            model_name='coursesession',
            name='student_feedback',
            field=models.TextField(blank=True, help_text='Student feedback for this lesson'),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='dive_schedule',
            field=models.ForeignKey(blank=True, help_text='Dive slot this lesson is scheduled in', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_sessions', to='users.diveschedule'),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='instructor',
            field=models.ForeignKey(blank=True, help_text='Primary instructor for this specific lesson', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_sessions', to='users.staff'),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='session_number',
            field=models.IntegerField(help_text='Lesson number in the course (1, 2, 3, etc.)'),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='status',
            field=models.CharField(choices=[('NOT_SCHEDULED', 'Not Scheduled'), ('SCHEDULED', 'Scheduled'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('RESCHEDULED', 'Rescheduled')], default='NOT_SCHEDULED', max_length=20),
        ),
        migrations.AlterField(
            model_name='coursesession',
            name='title',
            field=models.CharField(help_text="Lesson title (e.g., 'Pool Skills', 'Navigation Dive')", max_length=100),
        ),
        migrations.RenameField(
            model_name='courseenrollment',
            old_name='instructor',
            new_name='primary_instructor',
        ),
        migrations.AlterField(
            model_name='courseenrollment',
            name='primary_instructor',
            field=models.ForeignKey(blank=True, help_text='Main instructor responsible for this course', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_course_enrollments', to='users.staff'),
        ),
        migrations.AlterField(
            model_name='courseenrollment',
            name='start_date',
            field=models.DateField(blank=True, help_text='Date of first lesson', null=True),
        ),
    ]
