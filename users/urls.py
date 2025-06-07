from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    # path('users/', views.user_list, name='user_list'),
    # path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    # Diving Center URLs
    path('diving-center/', views.diving_center_dashboard, name='diving_center_dashboard'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/add/', views.add_activity, name='add_activity'),
    path('activities/<int:activity_id>/edit/', views.edit_activity, name='edit_activity'),
    path('activities/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
    path('calendar/', views.dive_calendar, name='dive_calendar'),
    path('calendar-view/', views.calendar_view, name='calendar_view'),
    path('schedule-dive/', views.schedule_dive, name='schedule_dive'),
    path('quick-schedule/', views.quick_schedule_dive, name='quick_schedule_dive'),
    path('dive/<int:dive_id>/participants/', views.manage_dive_participants, name='manage_dive_participants'),
    path('dive/<int:dive_id>/add-customer/', views.add_customer_to_dive, name='add_customer_to_dive'),
    path('dive/<int:dive_id>/', views.dive_detail, name='dive_detail'),
    path('customers/<int:customer_id>/history/', views.customer_activity_history, name='customer_activity_history'),
    path('dashboard-analytics/', views.dashboard_analytics, name='dashboard_analytics'),

    # Diving Sites
    path('diving-sites/', views.diving_sites_list, name='diving_sites_list'),
    path('diving-sites/add/', views.add_diving_site, name='add_diving_site'),

    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),

    # Diving Groups
    path('diving-groups/', views.diving_groups_list, name='diving_groups_list'),
    path('diving-groups/add/', views.add_diving_group, name='add_diving_group'),
    path('diving-groups/<int:group_id>/members/', views.manage_group_members, name='manage_group_members'),

    # Edit/Delete Dives
    path('dives/<int:dive_id>/edit/', views.edit_dive, name='edit_dive'),
    path('dives/<int:dive_id>/delete/', views.delete_dive, name='delete_dive'),

    # Medical Form (public access)
    path('medical-form/', views.medical_form, name='medical_form'),
    path('medical-forms/', views.medical_forms_list, name='medical_forms_list'),
    path('quick-edit-customer/<int:customer_id>/', views.quick_edit_customer, name='quick_edit_customer'),
    path('dive/<int:dive_id>/print/', views.print_participants, name='print_participants'),

    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:staff_id>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:staff_id>/edit/', views.edit_staff, name='edit_staff'),
    path('staff/<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),
    path('staff/planning/', views.staff_planning, name='staff_planning'),

    # Course Management
    # Pagina para listar los cursos
    path('courses/', views.courses_list, name='courses_list'),
    # Pagina para agregar un nuevo curso
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('course-enrollments/', views.course_enrollments, name='course_enrollments'),
    # Vista que controla el formulario
    path('customers/<int:customer_id>/enroll/', views.enroll_customer, name='enroll_customer'),
    path('enroll/', views.enroll_customer, name='enroll_customer_general'),
    path('enrollments/<int:enrollment_id>/', views.enrollment_detail, name='enrollment_detail'),
    path('course-sessions/<int:session_id>/schedule/', views.schedule_course_session, name='schedule_course_session'),
    path('course-sessions/<int:session_id>/complete/', views.complete_course_session, name='complete_course_session'),
    path('course-lesson-calendar/', views.course_lesson_calendar, name='course_lesson_calendar'),

    path('courses/<int:course_id>/sessions/add/', views.add_course_session_template, name='add_course_session_template'),
    path('courses/<int:course_id>/sessions/<int:session_id>/', views.get_course_session_template, name='get_course_session_template'),
    path('courses/<int:course_id>/sessions/<int:session_id>/update/', views.update_course_session_template, name='update_course_session_template'),
    path('courses/<int:course_id>/sessions/<int:session_id>/delete/', views.delete_course_session_template, name='delete_course_session_template'),
    path('enrollments/<int:enrollment_id>/sessions/add/', views.add_enrollment_session, name='add_enrollment_session'),

    path('customers/<int:customer_id>/courses/', views.customer_courses, name='customer_courses'),
    path('customers/<int:customer_id>/medical-detail/', views.customer_medical_detail, name='customer_medical_detail'),
    path('customers/<int:customer_id>/medical-form/download/', views.download_medical_form_pdf, name='download_medical_form'),
]