
# Generated migration file

from django.db import migrations


def migrate_activities_to_courses(apps, schema_editor):
    DiveActivity = apps.get_model('users', 'DiveActivity')
    Course = apps.get_model('users', 'Course')
    CustomerDiveActivity = apps.get_model('users', 'CustomerDiveActivity')
    
    # Create courses from existing activities
    activity_to_course_map = {}
    
    for activity in DiveActivity.objects.all():
        # Create corresponding course
        course, created = Course.objects.get_or_create(
            diving_center=activity.diving_center,
            name=activity.name,
            defaults={
                'description': activity.description,
                'total_dives': 1,
                'duration_days': max(1, activity.duration_minutes // 60) if activity.duration_minutes else 1,
                'price': activity.price,
                'course_type': 'CUSTOM',
                'is_active': True,
            }
        )
        activity_to_course_map[activity.id] = course.id
    
    # Update CustomerDiveActivity records
    for customer_activity in CustomerDiveActivity.objects.all():
        if customer_activity.activity_id and customer_activity.activity_id in activity_to_course_map:
            customer_activity.course_id = activity_to_course_map[customer_activity.activity_id]
            customer_activity.save()


def reverse_migrate_courses_to_activities(apps, schema_editor):
    # This is irreversible as we might lose data
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_course_to_customerdiveactivity'),
    ]

    operations = [
        migrations.RunPython(
            migrate_activities_to_courses,
            reverse_migrate_courses_to_activities,
        ),
    ]
