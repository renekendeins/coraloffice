from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(http_method_names=['get', 'post']), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
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
    path('analytics/', views.dashboard_analytics, name='dashboard_analytics'),
]

