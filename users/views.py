from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import calendar
import qrcode
import io
from .forms import SignUpForm, UserForm, UserProfileForm, CustomerForm, DiveScheduleForm, DiveActivityForm, CustomerDiveActivityForm, DivingSiteForm, InventoryItemForm, DivingGroupForm, MedicalForm, QuickCustomerForm, StaffForm, CourseForm, CourseEnrollmentForm, CourseSessionScheduleForm, LessonCompletionForm, MultipleCustomerEnrollmentForm, ScheduleMultipleSessionsForm
from .models import UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity, DivingSite, InventoryItem, DivingGroup, DivingGroupMember, Staff, Course, CourseEnrollment, CourseSession
from .utils import send_dive_reminder_email, send_welcome_email





def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Update user profile with diving center information
            if form.cleaned_data.get('is_diving_center'):
                user.userprofile.is_diving_center = True
                user.userprofile.business_name = form.cleaned_data.get(
                    'business_name', '')
                user.userprofile.business_license = form.cleaned_data.get(
                    'business_license', '')
                user.userprofile.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('users:profile')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def user_logout(request):
    logout(request)
    response = HttpResponseRedirect(reverse_lazy('users:profile'))
    response.delete_cookie('client')
    return response


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST,
                                       instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'users/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def user_list(request):
    users = User.objects.select_related('userprofile').all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/user_detail.html', {'profile_user': user})


@login_required
def diving_center_dashboard(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request,
                       'Access denied. This area is for diving centers only.')
        return redirect('users:profile')

    from datetime import date, timedelta

    customers = Customer.objects.filter(diving_center=request.user)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    upcoming_dives = DiveSchedule.objects.filter(
        diving_center=request.user,
        date__in=[today, tomorrow]
    ).order_by('date', 'time')

    return render(request, 'users/diving_center_dashboard.html', {
        'customers': customers,
        'upcoming_dives': upcoming_dives
    })


@login_required
def customer_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    customers = Customer.objects.filter(diving_center=request.user).order_by(
        '-created_at')

    # Handle search
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    customers_page = paginator.get_page(page_number)

    return render(request, 'users/customer_list.html', {
        'customers': customers_page,
        'search_query': search_query,
        'total_customers': customers.count()
    })


@login_required
def add_customer(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.diving_center = request.user
            customer.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('users:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'users/add_customer.html', {'form': form})


# @login_required
# def dive_calendar(request):
#     if not request.user.userprofile.is_diving_center:
#         messages.error(request, 'Access denied.')
#         return redirect('users:profile')

#     dives = DiveSchedule.objects.filter(diving_center=request.user).order_by(
#         'date', 'time')
#     return render(request, 'users/dive_calendar.html', {'dives': dives})


@login_required
def schedule_dive(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = DiveScheduleForm(diving_center=request.user, data=request.POST)
        if form.is_valid():
            dive = form.save(commit=False)
            dive.diving_center = request.user
            dive.save()
            messages.success(request, 'Dive scheduled successfully!')
            return redirect('users:calendar_view')
    else:
        form = DiveScheduleForm(diving_center=request.user)
    return render(request, 'users/schedule_dive.html', {'form': form})


@login_required
def edit_customer(request, customer_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    customer = get_object_or_404(Customer,
                                 id=customer_id,
                                 diving_center=request.user)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('users:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'users/edit_customer.html', {
        'form': form,
        'customer': customer
    })


@login_required
def delete_customer(request, customer_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    customer = get_object_or_404(Customer,
                                 id=customer_id,
                                 diving_center=request.user)

    if request.method == 'POST':
        customer_name = f"{customer.first_name} {customer.last_name}"
        customer.delete()
        messages.success(request,
                         f'Customer {customer_name} deleted successfully!')
        return redirect('users:customer_list')

    return render(request, 'users/delete_customer.html',
                  {'customer': customer})


@login_required
def activity_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    activities = DiveActivity.objects.filter(diving_center=request.user)
    return render(request, 'users/activity_list.html',
                  {'activities': activities})


@login_required
def add_activity(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = DiveActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.diving_center = request.user
            activity.save()
            messages.success(request, 'Activity added successfully!')
            return redirect('users:activity_list')
    else:
        form = DiveActivityForm()
    return render(request, 'users/add_activity.html', {'form': form})


@login_required
def edit_activity(request, activity_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    activity = get_object_or_404(DiveActivity,
                                 id=activity_id,
                                 diving_center=request.user)

    if request.method == 'POST':
        form = DiveActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully!')
            return redirect('users:activity_list')
    else:
        form = DiveActivityForm(instance=activity)
    return render(request, 'users/edit_activity.html', {
        'form': form,
        'activity': activity
    })


@login_required
def delete_activity(request, activity_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    activity = get_object_or_404(DiveActivity,
                                 id=activity_id,
                                 diving_center=request.user)

    if request.method == 'POST':
        activity_name = activity.name
        activity.delete()
        messages.success(request,
                         f'Activity "{activity_name}" deleted successfully!')
        return redirect('users:activity_list')

    return render(request, 'users/delete_activity.html',
                  {'activity': activity})


@login_required
def calendar_view(request):
    from django.db.models import Prefetch
    import time
    start_time = time.time()

    user = request.user
    profile = getattr(user, 'userprofile', None)
    if not profile or not profile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    today = datetime.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Generate calendar matrix and labels
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    is_current_month = (year == today.year and month == today.month)

    # Fetch dives efficiently
    dives = (
        DiveSchedule.objects
        .filter(diving_center=user, date__year=year, date__month=month)
        .select_related('diving_center')
        .prefetch_related('customer_activities__customer')  # for get_participant_count()
        .order_by('time')
    )

    # Collect all group info in advance to reduce queries in get_participant_count
    # Optional: Monkey patch a faster get_participant_count() for this view
    from collections import defaultdict

    # Group dive IDs to optimize counting
    dives_by_day = defaultdict(list)
    for dive in dives:
        # Highly optimized version assumes the function is already efficient
        dive.participant_count = dive.get_participant_count()
        dives_by_day[dive.date.day].append(dive)

    # Prepare context
    context = {
        'view_type': 'month',
        'calendar': cal,
        'month_name': month_name,
        'year': year,
        'month': month,
        'dives_by_day': dives_by_day,
        'today': today.day if is_current_month else None,
        'prev_month': 12 if month == 1 else month - 1,
        'prev_year': year - 1 if month == 1 else year,
        'next_month': 1 if month == 12 else month + 1,
        'next_year': year + 1 if month == 12 else year,
    }

    print(f"Execution time: {time.time() - start_time:.6f} seconds")
    return render(request, 'users/calendar_view.html', context)



@login_required
def quick_schedule_dive(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    selected_date = request.GET.get('date')

    if request.method == 'POST':
        form = DiveScheduleForm(diving_center=request.user, data=request.POST)
        if form.is_valid():
            dive = form.save(commit=False)
            dive.diving_center = request.user
            dive.save()
            messages.success(request, 'Dive scheduled successfully!')
            return redirect('users:calendar_view')
    else:
        initial_data = {}
        if selected_date:
            initial_data['date'] = selected_date
        form = DiveScheduleForm(diving_center=request.user, initial=initial_data)

    return render(request, 'users/quick_schedule_dive.html', {
        'form': form,
        'selected_date': selected_date
    })


@login_required
def manage_dive_participants(request, dive_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    dive = get_object_or_404(DiveSchedule,
                             id=dive_id,
                             diving_center=request.user)
    participants = CustomerDiveActivity.objects.filter(dive_schedule=dive)

    if request.method == 'POST':
        # Handle participant removal
        if 'remove_participant' in request.POST:
            participant_id = request.POST.get('customer')
            if participant_id:
                participant = get_object_or_404(CustomerDiveActivity, id=int(participant_id))
                participant.delete()
                messages.success(request, 'Participant removed from the dive!')
                return redirect('users:manage_dive_participants', dive_id=dive.id)

        # Handle on board action
        elif 'on_board' in request.POST:
            participant_id = request.POST.get('participant_id')
            if participant_id:
                participant = get_object_or_404(CustomerDiveActivity, id=int(participant_id))
                participant.status = 'ON_BOARD'
                participant.save()
                messages.success(request, f'{participant.customer} está presente!')
                return redirect('users:manage_dive_participants', dive_id=dive.id)

        # Handle back on boat action
        elif 'back_on_boat' in request.POST:
            participant_id = request.POST.get('participant_id')
            if participant_id:
                participant = get_object_or_404(CustomerDiveActivity, id=int(participant_id))
                participant.status = 'BACK_ON_BOAT'
                participant.save()
                messages.success(request, f'{participant.customer} is back on boat!')
                return redirect('users:manage_dive_participants', dive_id=dive.id)

        # Handle quick update participant
        elif 'quick_update_participant' in request.POST:
            participant_id = request.POST.get('participant_id')
            if participant_id:
                participant = get_object_or_404(CustomerDiveActivity, id=int(participant_id))

                # Update course if provided
                course_id = request.POST.get('course')
                if course_id:
                    course = get_object_or_404(Course, id=int(course_id), diving_center=request.user)
                    participant.course = course

                participant.tank_size = request.POST.get('tank_size', participant.tank_size)
                participant.status = request.POST.get('status', participant.status)
                participant.needs_wetsuit = 'needs_wetsuit' in request.POST
                participant.needs_bcd = 'needs_bcd' in request.POST
                participant.needs_regulator = 'needs_regulator' in request.POST
                participant.needs_guide = 'needs_guide' in request.POST
                participant.needs_insurance = 'needs_insurance' in request.POST                
                participant.needs_fins = 'needs_fins' in request.POST

                participant.is_paid = 'is_paid' in request.POST
                participant.save()
                messages.success(request, 'Participant updated successfully!')
                return redirect('users:manage_dive_participants', dive_id=dive.id)

        # Handle adding a participant or group
        elif 'add_participant' in request.POST:
            form = CustomerDiveActivityForm(diving_center=request.user, dive_schedule=dive, data=request.POST)
            if form.is_valid():
                selected_group = form.cleaned_data.get('selected_group')
                if selected_group:
                    # Check if dive can accommodate the entire group size
                    if not dive.can_accommodate_group(selected_group.group_size):
                        messages.error(request, f'No hay suficientes plazas disponibles. El grupo necesita {selected_group.group_size} plazas pero solo hay {dive.get_available_spots()} disponibles.')
                        return redirect('users:manage_dive_participants', dive_id=dive.id)
                    
                    # Initialize variables
                    emails_sent = 0

                    # Create or get a placeholder customer for this group
                    placeholder_customer, created = Customer.objects.get_or_create(
                        diving_center=request.user,
                        first_name=f"GRUPO-{selected_group.name}",
                        last_name="PLACEHOLDER",
                        defaults={
                            'email': f"placeholder-{selected_group.id}@grupo.temp",
                            'phone_number': "000000000",
                            'country': selected_group.country,
                            'language': 'ES',
                            'certification_level': 'NONE',
                            'default_tank_size': form.cleaned_data['tank_size']
                        }
                    )

                    # Check if placeholder not already participating
                    if not CustomerDiveActivity.objects.filter(dive_schedule=dive, customer=placeholder_customer).exists():
                        # Create ONE placeholder entry that represents the entire group
                        course = form.cleaned_data['course']

                        # Auto-set equipment needs if course includes material
                        needs_wetsuit = form.cleaned_data['needs_wetsuit']
                        needs_bcd = form.cleaned_data['needs_bcd']
                        needs_regulator = form.cleaned_data['needs_regulator']

                        if course and course.includes_material:
                            needs_wetsuit = True
                            needs_bcd = True
                            needs_regulator = True

                        CustomerDiveActivity.objects.create(
                            customer=placeholder_customer,
                            dive_schedule=dive,
                            course=course,
                            tank_size=form.cleaned_data['tank_size'],
                            needs_wetsuit=needs_wetsuit,
                            needs_bcd=needs_bcd,
                            needs_regulator=needs_regulator,
                            needs_guide=form.cleaned_data['needs_guide'],
                            needs_insurance=form.cleaned_data['needs_insurance'],
                            status='PENDING'
                        )

                        # Get group members for sending emails only
                        group_members = DivingGroupMember.objects.filter(group=selected_group)
                        
                        # Send reminder emails to group members (but don't add them as separate participants)
                        emails_sent = 0
                        for member in group_members:
                            if send_dive_reminder_email(member.customer, dive, course):
                                emails_sent += 1

                    success_msg = f'Añadido grupo {selected_group.name} a la inmersión! {selected_group.group_size} plazas reservadas.'
                    if emails_sent > 0:
                        success_msg += f' {emails_sent} emails de recordatorio enviados.'
                    messages.success(request, success_msg)
                else:
                    # Add single participant
                    participant = form.save(commit=False)
                    participant.dive_schedule = dive
                    # Use customer's default tank size if not specified
                    if not participant.tank_size and participant.customer.default_tank_size:
                        participant.tank_size = participant.customer.default_tank_size

                    # Auto-set equipment needs if course includes material
                    if participant.course and participant.course.includes_material:
                        participant.needs_wetsuit = True
                        participant.needs_bcd = True
                        participant.needs_regulator = True

                    participant.save()

                    # Send reminder email
                    email_sent = send_dive_reminder_email(participant.customer, dive, participant.course)
                    if email_sent:
                        messages.success(request, 'Participant added to dive! Reminder email sent.')
                    else:
                        messages.success(request, 'Participant added to dive!')
                return redirect('users:manage_dive_participants', dive_id=dive.id)
            else:
                messages.error(request, 'Please correct the form errors.')

        # Handle adding new customer
        elif 'add_new_customer' in request.POST:
            customer_form = CustomerForm(request.POST)
            if customer_form.is_valid():
                customer = customer_form.save(commit=False)
                customer.diving_center = request.user
                customer.save()
                messages.success(request, 'New customer added successfully!')
                return redirect('users:manage_dive_participants', dive_id=dive.id)
    else:
        form = CustomerDiveActivityForm(diving_center=request.user, dive_schedule=dive)

    customer_form = CustomerForm()

    return render(request, 'users/manage_dive_participants.html', {
        'dive': dive,
        'participants': participants,
        'form': form,
        'customer_form': customer_form,
        'tank_size_choices': CustomerDiveActivity.TANK_SIZE_CHOICES,
        'status_choices': CustomerDiveActivity.STATUS_CHOICES,
    })


@login_required
def add_customer_to_dive(request, dive_id):
    dive = get_object_or_404(DiveSchedule,
                             id=dive_id,
                             diving_center=request.user)

    if request.method == 'POST':
        form = CustomerDiveActivityForm(diving_center=request.user,
                                        dive_schedule=dive,
                                        data=request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.dive_schedule = dive
            participant.save()
            messages.success(request, 'Cliente añadido a la salida!')
            return redirect('users:manage_dive_participants', dive_id=dive.id)
    else:
        form = CustomerDiveActivityForm(diving_center=request.user,
                                        dive_schedule=dive)

    return render(request, 'users/add_customer_to_dive.html', {
        'dive': dive,
        'form': form
    })


@login_required
def dive_detail(request, dive_id):
    dive = get_object_or_404(DiveSchedule,
                             id=dive_id,
                             diving_center=request.user)
    participants = CustomerDiveActivity.objects.filter(dive_schedule=dive)

    # Calculate actual participant count considering group sizes
    actual_participant_count = dive.get_participant_count()

    # Calculate equipment counts
    equipment_counts = {
        'wetsuits': participants.filter(needs_wetsuit=True).count(),
        'bcds': participants.filter(needs_bcd=True).count(),
        'regulators': participants.filter(needs_regulator=True).count(),        
        'fins': participants.filter(needs_fins=True).count(),
        'guides': participants.filter(needs_guide=True).count(),
        'insurance': participants.filter(needs_insurance=True).count(),
    }

    # Calculate tank counts by size
    from django.db.models import Count
    tank_counts = participants.values('tank_size').annotate(
        count=Count('tank_size')
    ).order_by('tank_size')

    if request.method == 'POST':
        # Handle updating the dive details logic here if needed
        # Example (pseudo-code to update dive details):
        # Could be handled via a form, similar to adding or updating dives
        pass

    return render(request, 'users/dive_detail.html', {
        'dive': dive,
        'participants': participants,
        'equipment_counts': equipment_counts,
        'tank_counts': tank_counts,
        'actual_participant_count': actual_participant_count,
    })


@login_required
def customer_activity_history(request, customer_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    customer = get_object_or_404(Customer,
                                 id=customer_id,
                                 diving_center=request.user)

    activities = CustomerDiveActivity.objects.filter(
        customer=customer
    ).order_by('-dive_schedule__date', '-dive_schedule__time')

    return render(request, 'users/customer_activity_history.html', {
        'customer': customer,
        'activities': activities
    })


@login_required
def dashboard_analytics(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    from django.db.models import Count, Avg
    from datetime import date, datetime
    import json
    import calendar as cal

    customers = Customer.objects.filter(diving_center=request.user)
    activities = CustomerDiveActivity.objects.filter(
        customer__diving_center=request.user
    )
    schedules = DiveSchedule.objects.filter(diving_center=request.user)

    # Age range analysis
    age_ranges = {
        '18-25': 0,
        '26-35': 0,
        '36-45': 0,
        '46-55': 0,
        '55+': 0,
        'Unknown': 0
    }

    for customer in customers:
        age = customer.get_age()
        if age is None:
            age_ranges['Unknown'] += 1
        elif 18 <= age <= 25:
            age_ranges['18-25'] += 1
        elif 26 <= age <= 35:
            age_ranges['26-35'] += 1
        elif 36 <= age <= 45:
            age_ranges['36-45'] += 1
        elif 46 <= age <= 55:
            age_ranges['46-55'] += 1
        else:
            age_ranges['55+'] += 1

    # Activities per customer
    activities_per_customer = activities.values('customer').annotate(
        activity_count=Count('id')
    ).aggregate(avg_activities=Avg('activity_count'))

    # Activities by date for timeline chart
    activities_by_date = activities.values(
        'dive_schedule__date'
    ).annotate(
        count=Count('id')
    ).order_by('dive_schedule__date')

    # Prepare data for activities over time chart
    date_labels = [item['dive_schedule__date'].strftime('%Y-%m-%d') for item in activities_by_date]
    date_counts = [item['count'] for item in activities_by_date]

    # Activities scheduled by month (current year)
    current_year = datetime.now().year
    monthly_activities = {}
    year_to_date_total = 0

    for month in range(1, 13):
        month_count = schedules.filter(
            date__year=current_year,
            date__month=month
        ).count()
        monthly_activities[cal.month_name[month]] = month_count
        if month <= datetime.now().month:
            year_to_date_total += month_count

    # Total activities scheduled from beginning of year
    total_activities_year = schedules.filter(date__year=current_year).count()

    # Country data
    countries_data = customers.values('country').annotate(
        count=Count('id')
    ).order_by('-count')
    countries = {item['country'] or 'Unknown': item['count'] for item in countries_data}

    # Language data
    languages_data = customers.values('language').annotate(
        count=Count('id')
    ).order_by('-count')
    languages = {dict(Customer.LANGUAGE_CHOICES).get(item['language'], item['language']): item['count'] for item in languages_data}

    context = {
        'total_customers': customers.count(),
        'total_activities': activities.count(),
        'age_ranges': age_ranges,
        'avg_activities': activities_per_customer['avg_activities'] or 0,
        'countries': countries,
        'languages': languages,
        'date_labels': json.dumps(date_labels),
        'date_counts': json.dumps(date_counts),
        'monthly_activities': monthly_activities,
        'total_activities_year': total_activities_year,
        'year_to_date_total': year_to_date_total,
        'current_year': current_year,
    }

    return render(request, 'users/dashboard_analytics.html', context)


# Diving Sites Management
@login_required
def diving_sites_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    sites = DivingSite.objects.filter(diving_center=request.user)
    return render(request, 'users/diving_sites_list.html', {'sites': sites})


@login_required
def add_diving_site(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = DivingSiteForm(request.POST)
        if form.is_valid():
            site = form.save(commit=False)
            site.diving_center = request.user
            site.save()
            messages.success(request, 'Diving site added successfully!')
            return redirect('users:diving_sites_list')
    else:
        form = DivingSiteForm()
    return render(request, 'users/add_diving_site.html', {'form': form})


@login_required
def edit_diving_site(request, site_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    site = get_object_or_404(DivingSite, id=site_id, diving_center=request.user)

    if request.method == 'POST':
        form = DivingSiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diving site updated successfully!')
            return redirect('users:diving_sites_list')
    else:
        form = DivingSiteForm(instance=site)
    return render(request, 'users/edit_diving_site.html', {'form': form, 'site': site})


@login_required
def delete_diving_site(request, site_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    site = get_object_or_404(DivingSite, id=site_id, diving_center=request.user)

    if request.method == 'POST':
        site_name = site.name
        site.delete()
        messages.success(request, f'Diving site "{site_name}" deleted successfully!')
        return redirect('users:diving_sites_list')

    return render(request, 'users/delete_diving_site.html', {'site': site})


# Inventory Management
@login_required
def inventory_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    items = InventoryItem.objects.filter(diving_center=request.user)
    return render(request, 'users/inventory_list.html', {'items': items})


@login_required
def add_inventory_item(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.diving_center = request.user
            item.save()
            messages.success(request, 'Inventory item added successfully!')
            return redirect('users:inventory_list')
    else:
        form = InventoryItemForm()
    return render(request, 'users/add_inventory_item.html', {'form': form})


# Diving Groups Management
@login_required
def diving_groups_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    from datetime import date, timedelta
    from django.db.models import Q

    groups = DivingGroup.objects.filter(diving_center=request.user)

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Country filter
    country_filter = request.GET.get('country', '').strip()
    if country_filter:
        groups = groups.filter(country=country_filter)

    # Date filters
    date_filter = request.GET.get('date_filter', '').strip()
    today = date.today()

    if date_filter == 'arriving_soon':
        # Groups arriving in the next 7 days
        next_week = today + timedelta(days=7)
        groups = groups.filter(
            arrival_date__gte=today,
            arrival_date__lte=next_week
        )
    elif date_filter == 'currently_here':
        # Groups currently staying (arrival date passed, departure date not yet reached)
        groups = groups.filter(
            arrival_date__lte=today,
            departure_date__gte=today
        )
    elif date_filter == 'departing_soon':
        # Groups departing in the next 7 days
        next_week = today + timedelta(days=7)
        groups = groups.filter(
            departure_date__gte=today,
            departure_date__lte=next_week
        )
    elif date_filter == 'past_groups':
        # Groups that have already departed
        groups = groups.filter(departure_date__lt=today)

    # Sorting
    sort_by = request.GET.get('sort_by', '-created_at')
    valid_sort_fields = [
        'name', '-name', 'created_at', '-created_at', 
        'arrival_date', '-arrival_date', 'country', '-country'
    ]

    if sort_by in valid_sort_fields:
        groups = groups.order_by(sort_by)
    else:
        groups = groups.order_by('-created_at')

    # Get country choices for the filter dropdown
    country_choices = Customer.COUNTRY_CHOICES

    context = {
        'groups': groups,
        'country_choices': country_choices,
        'search_query': search_query,
    }

    return render(request, 'users/diving_groups_list.html', context)


@login_required
def add_diving_group(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = DivingGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.diving_center = request.user
            group.save()
            messages.success(request, 'Diving group added successfully!')
            return redirect('users:diving_groups_list')
    else:
        form = DivingGroupForm()
    return render(request, 'users/add_diving_group.html', {'form': form})


@login_required
def manage_group_members(request, group_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    group = get_object_or_404(DivingGroup, id=group_id, diving_center=request.user)
    members = DivingGroupMember.objects.filter(group=group).order_by('-is_leader', 'customer__first_name', 'customer__last_name')
    courses = Course.objects.all().order_by('-just_one_dive', 'name')
    available_customers = Customer.objects.filter(diving_center=request.user).exclude(
        id__in=members.values_list('customer_id', flat=True)
    )

    # Available dives are now loaded via AJAX for better performance

    if request.method == 'POST':
        if 'add_member' in request.POST:
            customer_id = request.POST.get('customer_id')
            if customer_id:
                customer = get_object_or_404(Customer, id=customer_id, diving_center=request.user)
                DivingGroupMember.objects.create(group=group, customer=customer)
                messages.success(request, f'{customer} added to group!')
                return redirect('users:manage_group_members', group_id=group.id)

        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            if member_id:
                member = get_object_or_404(DivingGroupMember, id=member_id, group=group)
                member.delete()
                messages.success(request, 'Member removed from group!')
                return redirect('users:manage_group_members', group_id=group.id)

        elif 'set_leader' in request.POST:
            member_id = request.POST.get('member_id')
            if member_id:
                # Remove current leader status from all members
                DivingGroupMember.objects.filter(group=group).update(is_leader=False)
                # Set new leader
                member = get_object_or_404(DivingGroupMember, id=member_id, group=group)
                member.is_leader = True
                member.save()
                messages.success(request, f'{member.customer} is now the group leader!')
                return redirect('users:manage_group_members', group_id=group.id)

        elif 'add_new_customer_to_group' in request.POST:
            quick_customer_form = QuickCustomerForm(request.POST)
            if quick_customer_form.is_valid():
                customer = quick_customer_form.save(commit=False)
                customer.diving_center = request.user
                customer.save()
                DivingGroupMember.objects.create(group=group, customer=customer)
                messages.success(request, f'New customer {customer} created and added to group!')
                return redirect('users:manage_group_members', group_id=group.id)
            else:
                messages.error(request, 'Please correct the form errors.')

        elif 'schedule_group' in request.POST:
            # Handle both old format (getlist) and new format (comma-separated string)
            dive_ids_str = request.POST.get('selected_dives', '')
            if dive_ids_str:
                dive_ids = dive_ids_str.split(',')
            else:
                dive_ids = request.POST.getlist('selected_dives')
            
            course_id = request.POST.get('course_id')
            needs_wetsuit = 'needs_wetsuit' in request.POST
            needs_bcd = 'needs_bcd' in request.POST
            needs_regulator = 'needs_regulator' in request.POST
            needs_guide = 'needs_guide' in request.POST
            needs_insurance = 'needs_insurance' in request.POST

            if dive_ids and course_id:
                course = get_object_or_404(Course, id=course_id, diving_center=request.user)
                scheduled_count = 0
                # emails_sent = 0
                skipped_dives = []

                for dive_id in dive_ids:
                    dive = get_object_or_404(DiveSchedule, id=dive_id, diving_center=request.user)

                    # Check if dive can accommodate the entire group size
                    if not dive.can_accommodate_group(group.group_size):
                        skipped_dives.append(f"{dive.dive_site.name} ({dive.date} {dive.time}) - Solo {dive.get_available_spots()} plazas disponibles, pero el grupo necesita {group.group_size}")
                        continue

                    # Create or get a placeholder customer for this group
                    placeholder_customer, created = Customer.objects.get_or_create(
                        diving_center=request.user,
                        first_name=f"GRUPO-{group.name}",
                        last_name="PLACEHOLDER",
                        defaults={
                            'email': f"placeholder-{group.id}@grupo.temp",
                            'phone_number': "000000000",
                            'country': group.country,
                            'language': 'ES',
                            'certification_level': 'NONE',
                            'default_tank_size': '12L'
                        }
                    )

                    # Check if placeholder not already in this dive
                    if not CustomerDiveActivity.objects.filter(
                        dive_schedule=dive, 
                        customer=placeholder_customer
                    ).exists():
                        CustomerDiveActivity.objects.create(
                            customer=placeholder_customer,
                            dive_schedule=dive,
                            course=course,
                            tank_size='12L',
                            needs_wetsuit=needs_wetsuit,
                            needs_bcd=needs_bcd,
                            needs_regulator=needs_regulator,
                            needs_guide=needs_guide,
                            needs_insurance=needs_insurance,
                            status='PENDING'
                        )
                        scheduled_count += 1

                    # Send reminder emails to group members (but don't add them as separate participants)
                    # for member in members:
                    #     if send_dive_reminder_email(member.customer, dive, course):
                    #         emails_sent += 1

                success_msg = f'Programado {group.name} para {len(dive_ids) - len(skipped_dives)} inmersión(es)! Añadidos {scheduled_count} espacios, reservadas {group.group_size * (len(dive_ids) - len(skipped_dives))} plazas en total.'
                # if emails_sent > 0:
                #     success_msg += f' {emails_sent} emails de recordatorio enviados.'

                if skipped_dives:
                    messages.warning(request, f'Algunas inmersiones fueron omitidas por falta de capacidad: {"; ".join(skipped_dives)}')

                messages.success(request, success_msg)
                return redirect('users:manage_group_members', group_id=group.id)
            else:
                messages.error(request, 'Please select at least one dive and an activity.')

    # Get group activities and tank size choices for the form
    group_courses = Course.objects.filter(diving_center=request.user).order_by('-just_one_dive', 'name')
    tank_choices = CustomerDiveActivity.TANK_SIZE_CHOICES
    quick_customer_form = QuickCustomerForm()

    return render(request, 'users/manage_group_members.html', {
        'group': group,
        'members': members,
        'courses': courses,
        'available_customers': available_customers,
        'group_courses': group_courses,
        'tank_choices': tank_choices,
        'quick_customer_form': quick_customer_form,
    })


# Edit and Delete Dive Views
@login_required
def edit_dive(request, dive_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    dive = get_object_or_404(DiveSchedule, id=dive_id, diving_center=request.user)

    if request.method == 'POST':
        form = DiveScheduleForm(diving_center=request.user, data=request.POST, instance=dive)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dive updated successfully!')
            return redirect('users:dive_detail', dive_id=dive.id)
    else:
        form = DiveScheduleForm(diving_center=request.user, instance=dive)

    return render(request, 'users/edit_dive.html', {'form': form, 'dive': dive})


@login_required
def delete_dive(request, dive_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    dive = get_object_or_404(DiveSchedule, id=dive_id, diving_center=request.user)

    if request.method == 'POST':
        dive_info = f"{dive.dive_site} on {dive.date}"
        dive.delete()
        messages.success(request, f'Dive "{dive_info}" deleted successfully!')
        return redirect('users:calendar_view')

    return render(request, 'users/delete_dive.html', {'dive': dive})


@login_required
def medical_forms_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    medical_forms = Customer.objects.filter(diving_center=request.user).order_by('-created_at')

    # Handle search
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        medical_forms = medical_forms.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(medical_forms, 10)  # Show 10 forms per page
    page_number = request.GET.get('page')
    medical_forms_page = paginator.get_page(page_number)

    return render(request, 'users/medical_forms_list.html', {
        'medical_forms': medical_forms_page,
        'search_query': search_query,
        'total_forms': medical_forms.count()
    })


# Medical Form (accessible without login)
def medical_form(request, dive_center_uuid=None):
    diving_center = None
    if dive_center_uuid:
        try:
            diving_center = User.objects.get(userprofile__uuid=dive_center_uuid, userprofile__is_diving_center=True)
        except User.DoesNotExist:
            messages.error(request, 'Invalid diving center link.')
            return redirect('home:index')
    else:
        # Fallback to first diving center for backward compatibility
        diving_center = User.objects.filter(userprofile__is_diving_center=True).first()

    if request.method == 'POST':
        form = MedicalForm(request.POST)
        if form.is_valid():
            if diving_center:
                customer = form.save(commit=False)
                customer.diving_center = diving_center

                # Handle signature data
                signature_data = request.POST.get('signature')
                if signature_data and signature_data.startswith('data:image/png;base64,'):
                    import base64
                    from django.core.files.base import ContentFile
                    import uuid

                    # Remove the data URL prefix
                    format, imgstr = signature_data.split(';base64,')
                    ext = format.split('/')[-1]

                    # Decode the base64 image
                    data = ContentFile(base64.b64decode(imgstr))

                    # Generate a unique filename
                    filename = f"signature_{uuid.uuid4().hex}.{ext}"

                    # Save the signature
                    customer.signature.save(filename, data, save=False)

                customer.save()

                # Send welcome email
                email_sent = send_welcome_email(customer)
                if email_sent:
                    messages.success(request, 'Formulario médico enviado con éxito! Se te ha enviado un correo electrónico de bienvenida.')
                else:
                    messages.success(request, 'Formulario médico enviado con éxito!')

                return redirect('users:medical_form')
            else:
                messages.error(request, 'Hubo un problema al enviar el formulario. Por favor, inténtalo de nuevo.')
    else:
        form = MedicalForm()

    context = {
        'form': form,
        'diving_center': diving_center,
        'dive_center_uuid': dive_center_uuid
    }
    return render(request, 'users/medical_form.html', context)


@login_required
def print_participants(request, dive_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    dive = get_object_or_404(DiveSchedule, id=dive_id, diving_center=request.user)
    participants = CustomerDiveActivity.objects.filter(dive_schedule=dive).order_by('customer__last_name', 'customer__first_name')

    # Calculate equipment summary
    equipment_summary = {
        'total_participants': participants.count(),
        'tanks_by_size': {},
        'wetsuits_by_size': {},
        'bcds_by_size': {},
        'fins_by_size': {},
        'regulators_needed': participants.filter(needs_regulator=True).count(),
        'guides_needed': participants.filter(needs_guide=True).count(),
        'insurance_needed': participants.filter(needs_insurance=True).count(),
    }

    # Count tanks by size
    for participant in participants:
        tank_size = participant.tank_size
        if tank_size not in equipment_summary['tanks_by_size']:
            equipment_summary['tanks_by_size'][tank_size] = 0
        equipment_summary['tanks_by_size'][tank_size] += 1

    # Count equipment by size for participants who need them
    for participant in participants:
        if participant.needs_wetsuit:
            wetsuit_size = participant.customer.get_wetsuit_size()
            if wetsuit_size not in equipment_summary['wetsuits_by_size']:
                equipment_summary['wetsuits_by_size'][wetsuit_size] = 0
            equipment_summary['wetsuits_by_size'][wetsuit_size] += 1

        if participant.needs_bcd:
            bcd_size = participant.customer.get_bcd_size()
            if bcd_size not in equipment_summary['bcds_by_size']:
                equipment_summary['bcds_by_size'][bcd_size] = 0
            equipment_summary['bcds_by_size'][bcd_size] += 1

        if participant.needs_regulator:  # For fins, we count when regulators are needed (as proxy)
            fins_size = participant.customer.get_fins_size()
            if fins_size not in equipment_summary['fins_by_size']:
                equipment_summary['fins_by_size'][fins_size] = 0
            equipment_summary['fins_by_size'][fins_size] += 1

    context = {
        'dive': dive,
        'participants': participants,
        'equipment_summary': equipment_summary,
        'print_mode': True,
    }

    return render(request, 'users/print_participants.html', context)


# Staff Management Views
@login_required
def staff_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    staff_members = Staff.objects.filter(diving_center=request.user).order_by('first_name', 'last_name')
    return render(request, 'users/staff_list.html', {'staff_members': staff_members})


@login_required
def add_staff(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff_member = form.save(commit=False)
            staff_member.diving_center = request.user
            staff_member.save()
            messages.success(request, 'Staff member added successfully!')
            return redirect('users:staff_list')
    else:
        form = StaffForm()
    return render(request, 'users/add_staff.html', {'form': form})


@login_required
def edit_staff(request, staff_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    staff_member = get_object_or_404(Staff, id=staff_id, diving_center=request.user)

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member updated successfully!')
            return redirect('users:staff_list')
    else:
        form = StaffForm(instance=staff_member)
    return render(request, 'users/edit_staff.html', {'form': form, 'staff_member': staff_member})


@login_required
def staff_detail(request, staff_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    staff_member = get_object_or_404(Staff, id=staff_id, diving_center=request.user)

    # Get all activities for this staff member
    activities = CustomerDiveActivity.objects.filter(
        assigned_staff=staff_member
    ).order_by('-dive_schedule__date', '-dive_schedule__time').select_related(
        'customer', 'dive_schedule', 'activity', 'dive_schedule__dive_site'
    )

    # Get upcoming activities
    from datetime import date
    upcoming_activities = activities.filter(dive_schedule__date__gte=date.today())
    past_activities = activities.filter(dive_schedule__date__lt=date.today())

    # Statistics
    total_activities = activities.count()
    upcoming_count = upcoming_activities.count()

    return render(request, 'users/staff_detail.html', {
        'staff_member': staff_member,
        'upcoming_activities': upcoming_activities,
        'past_activities': past_activities,
        'total_activities': total_activities,
        'upcoming_count': upcoming_count,
    })


@login_required
def delete_staff(request, staff_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    staff_member = get_object_or_404(Staff, id=staff_id, diving_center=request.user)

    if request.method == 'POST':
        staff_name = staff_member.get_full_name()
        staff_member.delete()
        messages.success(request, f'Staff member {staff_name} deleted successfully!')
        return redirect('users:staff_list')

    return render(request, 'users/delete_staff.html', {'staff_member': staff_member})


@login_required
def staff_planning(request):
    """Show planning for tomorrow's activities"""
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    from datetime import date, timedelta
    tomorrow = date.today() + timedelta(days=1)

    # Handle staff assignment
    if request.method == 'POST' and 'assign_staff_to_activity' in request.POST:
        activity_id = request.POST.get('activity_id')
        staff_id = request.POST.get('staff_id')

        if activity_id and staff_id:
            try:
                activity = CustomerDiveActivity.objects.get(
                    id=activity_id,
                    dive_schedule__diving_center=request.user
                )
                staff = Staff.objects.get(id=staff_id, diving_center=request.user)
                activity.assigned_staff = staff
                activity.save()
                messages.success(request, f'Successfully assigned {staff.get_full_name()} to {activity.customer.get_full_name()}\'s activity!')
            except (CustomerDiveActivity.DoesNotExist, Staff.DoesNotExist):
                messages.error(request, 'Invalid assignment. Please try again.')

        return redirect('users:staff_planning')

    # Get all dive schedules for tomorrow
    tomorrow_dives = DiveSchedule.objects.filter(
        diving_center=request.user,
        date=tomorrow
    ).order_by('time')

    # Get all customer activities for tomorrow with assigned staff
    tomorrow_activities = CustomerDiveActivity.objects.filter(
        dive_schedule__diving_center=request.user,
        dive_schedule__date=tomorrow
    ).select_related(
        'customer', 'assigned_staff', 'activity','course', 'dive_schedule', 'dive_schedule__dive_site'
    ).order_by('dive_schedule__time', 'assigned_staff__first_name')

    # Group activities by staff member
    staff_assignments = {}
    unassigned_activities = []

    for activity in tomorrow_activities:
        if activity.assigned_staff:
            staff_id = activity.assigned_staff.id
            if staff_id not in staff_assignments:
                staff_assignments[staff_id] = {
                    'staff': activity.assigned_staff,
                    'activities': []
                }
            staff_assignments[staff_id]['activities'].append(activity)
        else:
            unassigned_activities.append(activity)

    # Get all active staff members
    all_staff = Staff.objects.filter(diving_center=request.user, status='ACTIVE')

    return render(request, 'users/staff_planning.html', {
        'tomorrow': tomorrow,
        'tomorrow_dives': tomorrow_dives,
        'staff_assignments': staff_assignments.values(),
        'unassigned_activities': unassigned_activities,
        'all_staff': all_staff,
    })


@login_required
def quick_edit_customer(request, customer_id):
    """AJAX endpoint for quick editing customer details"""
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    customer = get_object_or_404(Customer, id=customer_id, diving_center=request.user)

    if request.method == 'POST':
        try:
            # Update customer fields
            customer.default_tank_size = request.POST.get('default_tank_size', customer.default_tank_size)

            weight = request.POST.get('weight')
            if weight:
                customer.weight = float(weight)

            height = request.POST.get('height')
            if height:
                customer.height = float(height)

            foot_size = request.POST.get('foot_size')
            if foot_size:
                customer.foot_size = float(foot_size)

            customer.save()

            return JsonResponse({
                'success': True,
                'tank_size': customer.default_tank_size,
                'wetsuit_size': customer.get_wetsuit_size(),
                'bcd_size': customer.get_bcd_size(),
                'fins_size': customer.get_fins_size()
            })

        except (ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': 'Invalid data provided'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})



# Course Management Views
@login_required
def courses_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    courses = Course.objects.filter(diving_center=request.user).order_by('name')
    return render(request, 'users/courses_list.html', {'courses': courses})

@login_required
def add_course(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.diving_center = request.user
            course.save()
            messages.success(request, 'Course added successfully!')
            return redirect('users:courses_list')
    else:
        form = CourseForm()
    return render(request, 'users/add_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    course = get_object_or_404(Course, id=course_id, diving_center=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('users:courses_list')
    else:
        form = CourseForm(instance=course)

    # Get template sessions for this course (sessions not tied to any enrollment)
    template_sessions = CourseSession.objects.filter(
        enrollment__isnull=True,
        template_course=course
    ).order_by('session_number')

    # Get current enrollments for this course
    enrollments = CourseEnrollment.objects.filter(course=course).select_related('customer')

    return render(request, 'users/edit_course.html', {
        'form': form, 
        'course': course,
        'template_sessions': template_sessions,
        'enrollments': enrollments
    })

@login_required
def course_enrollments(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    enrollments = CourseEnrollment.objects.filter(
        course__diving_center=request.user
    ).exclude(
        status__in=["COMPLETED", "CANCELLED"]
    ).select_related(
        'customer', 'course', 'primary_instructor'
    ).order_by('-created_at')

    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)

    return render(request, 'users/course_enrollments.html', {
        'enrollments': enrollments,
        'status_filter': status_filter,
        'status_choices': CourseEnrollment.STATUS_CHOICES
    })

@login_required
def enroll_customer(request, customer_id=None):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')
    customer = None
    print('customer id', customer_id)
    if customer_id:
        #customer = get_object_or_404(Customer, id=request.POST.get('customer'), diving_center=request.user)
        customer = get_object_or_404(Customer, id=customer_id, diving_center=request.user)


    if request.method == 'POST':
        form = CourseEnrollmentForm(diving_center=request.user, data=request.POST)

        if form.is_valid():
            enrollment = form.save()
            # Create course sessions based on template sessions or fallback to default
            course = enrollment.course

            template_sessions = CourseSession.objects.filter(template_course=course).order_by('session_number')
            if template_sessions.exists():
                # Use template sessions
                for template in template_sessions:
                    CourseSession.objects.create(
                        enrollment=enrollment,
                        session_number=template.session_number,
                        session_type=template.session_type,
                        title=template.title,
                        description=template.description,
                        skills_covered=template.skills_covered
                    )
            else:
                print('template_sessions does not exist')
                # Fallback to default sessions if no templates exist
                for i in range(1, course.total_dives + 1):
                    CourseSession.objects.create(
                        enrollment=enrollment,
                        session_number=i,
                        session_type='OPEN_WATER',
                        title=f'Dive {i}',
                        description=f'Dive session {i} of {course.name}'
                    )
            messages.success(request, f'{enrollment.customer} has been enrolled in {course.name}!')
            return redirect('users:course_enrollments')
        else:
            print('form invalid', form.errors)
    else:
        initial_data = {}
        if customer:
            initial_data['customer'] = customer

        # Auto-select course if passed as parameter
        course_id = request.GET.get('course')
        if course_id:
            try:
                course = Course.objects.get(id=course_id, diving_center=request.user)
                initial_data['course'] = course
            except Course.DoesNotExist:
                pass

        # Auto-select customer if passed as parameter
        customer_id = request.GET.get('customer')
        if customer_id:
            try:
                customer_obj = Customer.objects.get(id=customer_id, diving_center=request.user)
                initial_data['customer'] = customer_obj
            except Customer.DoesNotExist:
                pass

        form = CourseEnrollmentForm(diving_center=request.user, initial=initial_data)

    return render(request, 'users/enroll_customer.html', {
        'form': form,
        'customer': customer
    })


@login_required
def course_lesson_calendar(request):
    """View to show all scheduled course lessons in a calendar format"""
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    from datetime import date, timedelta
    today = date.today()
    start_date = today - timedelta(days=7)
    end_date = today + timedelta(days=30)

    # Get all scheduled course sessions
    scheduled_sessions = CourseSession.objects.filter(
        enrollment__course__diving_center=request.user,
        status__in=['SCHEDULED', 'IN_PROGRESS'],
        dive_schedule__date__range=[start_date, end_date]
    ).select_related(
        'enrollment__customer', 
        'enrollment__course', 
        'instructor', 
        'dive_schedule__dive_site'
    ).order_by('dive_schedule__date', 'dive_schedule__time')

    return render(request, 'users/course_lesson_calendar.html', {
        'scheduled_sessions': scheduled_sessions,
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
def enrollment_detail(request, enrollment_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    enrollment = get_object_or_404(
        CourseEnrollment,
        id=enrollment_id,
        course__diving_center=request.user
    )

    sessions = enrollment.course_sessions.all().order_by('session_number')

    return render(request, 'users/enrollment_detail.html', {
        'enrollment': enrollment,
        'sessions': sessions
    })

@login_required
def schedule_course_session(request, session_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    session = get_object_or_404(
        CourseSession,
        id=session_id,
        enrollment__course__diving_center=request.user
    )

    if request.method == 'POST':
        form = CourseSessionScheduleForm(diving_center=request.user, session=session, data=request.POST)
        if form.is_valid():
            dive_schedule = form.cleaned_data['dive_schedule']
            instructor = form.cleaned_data['instructor']
            assistant_instructors = form.cleaned_data['assistant_instructors']
            instructor_notes = form.cleaned_data['instructor_notes']

            # Update session details
            session.dive_schedule = dive_schedule
            session.scheduled_date = dive_schedule.date
            session.scheduled_time = dive_schedule.time
            session.instructor = instructor
            session.instructor_notes = instructor_notes
            session.status = 'SCHEDULED'
            session.save()

            # Set assistant instructors
            session.assistant_instructors.set(assistant_instructors)

            # Create CustomerDiveActivity for this course session using the enrollment's actual course
            defaults = {
                'course': session.enrollment.course,  # Use the actual course from enrollment
                'course_session': session,
                'assigned_staff': instructor,
                'tank_size': session.enrollment.customer.default_tank_size,
            }

            # Auto-set equipment needs if course includes material
            if session.enrollment.course.includes_material:
                defaults.update({
                    'needs_wetsuit': True,
                    'needs_bcd': True,
                    'needs_regulator': True,
                })

            customer_dive_activity, created = CustomerDiveActivity.objects.get_or_create(
                customer=session.enrollment.customer,
                dive_schedule=dive_schedule,
                defaults=defaults
            )

            if not created:
                customer_dive_activity.course = session.enrollment.course  # Update to use enrollment course
                customer_dive_activity.course_session = session
                customer_dive_activity.assigned_staff = instructor

                # Auto-set equipment needs if course includes material
                if session.enrollment.course.includes_material:
                    customer_dive_activity.needs_wetsuit = True
                    customer_dive_activity.needs_bcd = True
                    customer_dive_activity.needs_regulator = True

                customer_dive_activity.save()

            # Update enrollment status if needed
            session.enrollment.auto_update_status()

            messages.success(request, f'Lesson {session.session_number} scheduled successfully!')
            return redirect('users:enrollment_detail', enrollment_id=session.enrollment.id)
    else:
        form = CourseSessionScheduleForm(diving_center=request.user, session=session)

    return render(request, 'users/schedule_course_session.html', {
        'form': form,
        'session': session
    })

@login_required
def complete_course_session(request, session_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    session = get_object_or_404(
        CourseSession,
        id=session_id,
        enrollment__course__diving_center=request.user
    )

    if request.method == 'POST':
        form = LessonCompletionForm(request.POST)
        if form.is_valid():
            # Update session details
            session.grade = form.cleaned_data.get('grade', '')
            session.instructor_notes = form.cleaned_data.get('instructor_notes', '')
            session.student_feedback = form.cleaned_data.get('student_feedback', '')

            # Set completion date
            completion_date = form.cleaned_data.get('completion_date')
            if completion_date:
                session.completion_date = completion_date
            else:
                from django.utils import timezone
                session.completion_date = timezone.now()

            session.status = 'COMPLETED'
            session.save()

            # Update any related CustomerDiveActivity status
            if hasattr(session, 'dive_activities') and session.dive_activities.exists():
                for activity in session.dive_activities.all():
                    activity.status = 'FINISHED'
                    activity.save()

            # Update enrollment status automatically
            session.enrollment.auto_update_status()

            messages.success(request, f'Lesson {session.session_number} marked as completed!')
            return redirect('users:enrollment_detail', enrollment_id=session.enrollment.id)
        else:
            messages.error(request, 'Please correct the form errors.')
    else:
        form = LessonCompletionForm()

    return render(request, 'users/complete_course_session.html', {
        'form': form,
        'session': session
    })


@login_required
def add_course_session_template(request, course_id):
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    course = get_object_or_404(Course, id=course_id, diving_center=request.user)

    if request.method == 'POST':
        try:
            session_number = int(request.POST.get('session_number'))
            session_type = request.POST.get('session_type')
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            skills_covered = request.POST.get('skills_covered', '')

            # Check if session number already exists for this course template
            if CourseSession.objects.filter(template_course=course, session_number=session_number).exists():
                return JsonResponse({'success': False, 'error': 'Session number already exists'})

            session = CourseSession.objects.create(
                template_course=course,
                session_number=session_number,
                session_type=session_type,
                title=title,
                description=description,
                skills_covered=skills_covered
            )

            return JsonResponse({'success': True, 'session_id': session.id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def get_course_session_template(request, course_id, session_id):
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    course = get_object_or_404(Course, id=course_id, diving_center=request.user)
    session = get_object_or_404(CourseSession, id=session_id, template_course=course)

    data = {
        'session_number': session.session_number,
        'session_type': session.session_type,
        'title': session.title,
        'description': session.description,
        'skills_covered': session.skills_covered
    }

    return JsonResponse(data)

@login_required
def update_course_session_template(request, course_id, session_id):
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    course = get_object_or_404(Course, id=course_id, diving_center=request.user)
    session = get_object_or_404(CourseSession, id=session_id, template_course=course)

    if request.method == 'POST':
        try:
            session_number = int(request.POST.get('session_number'))

            # Check if session number already exists (excluding current session)
            existing = CourseSession.objects.filter(
                template_course=course, 
                session_number=session_number
            ).exclude(id=session_id)

            if existing.exists():
                return JsonResponse({'success': False, 'error': 'Session number already exists'})

            session.session_number = session_number
            session.session_type = request.POST.get('session_type')
            session.title = request.POST.get('title')
            session.description = request.POST.get('description', '')
            session.skills_covered = request.POST.get('skills_covered', '')
            session.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def delete_course_session_template(request, course_id, session_id):
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    course = get_object_or_404(Course, id=course_id, diving_center=request.user)
    session = get_object_or_404(CourseSession, id=session_id, template_course=course)

    if request.method == 'POST':
        try:
            session.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def add_enrollment_session(request, enrollment_id):
    """Add an extra session to an existing enrollment"""
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    enrollment = get_object_or_404(
        CourseEnrollment, 
        id=enrollment_id, 
        course__diving_center=request.user
    )

    if request.method == 'POST':
        try:
            session_number = int(request.POST.get('session_number'))
            session_type = request.POST.get('session_type')
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            skills_covered = request.POST.get('skills_covered', '')

            # Check if session number already exists for this enrollment
            if enrollment.course_sessions.filter(session_number=session_number).exists():
                return JsonResponse({'success': False, 'error': 'Session number already exists'})

            session = CourseSession.objects.create(
                enrollment=enrollment,
                session_number=session_number,
                session_type=session_type,
                title=title,
                description=description,
                skills_covered=skills_covered
            )

            return JsonResponse({'success': True, 'session_id': session.id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})



@login_required
def customer_courses(request, customer_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    customer = get_object_or_404(Customer, id=customer_id, diving_center=request.user)

    # Get all enrollments for this customer
    all_enrollments = CourseEnrollment.objects.filter(
        customer=customer
    ).select_related('course', 'primary_instructor').order_by('-enrollment_date')

    # Separate active and completed enrollments
    active_enrollments = all_enrollments.filter(status__in=['ENROLLED', 'IN_PROGRESS'])
    completed_enrollments = all_enrollments.filter(status='COMPLETED')

    return render(request, 'users/customer_courses.html', {
        'customer': customer,
        'active_enrollments': active_enrollments,
        'completed_enrollments': completed_enrollments,
        'all_enrollments': all_enrollments
    })


@login_required
def customer_medical_detail(request, customer_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    customer = get_object_or_404(Customer, id=customer_id, diving_center=request.user)

    return render(request, 'users/customer_medical_detail.html', {
        'customer': customer
    })

@login_required
def enroll_multiple_customers(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = MultipleCustomerEnrollmentForm(diving_center=request.user, data=request.POST)

        if form.is_valid():
            course = form.cleaned_data['course']
            customers = form.cleaned_data['customers']
            primary_instructor = form.cleaned_data.get('primary_instructor')
            start_date = form.cleaned_data.get('start_date')
            price_paid = form.cleaned_data.get('price_paid', 0.00)
            is_paid = form.cleaned_data.get('is_paid', False)
            notes = form.cleaned_data.get('notes', '')

            enrolled_count = 0
            skipped_count = 0

            for customer in customers:
                # Check if customer is already enrolled in this course
                if CourseEnrollment.objects.filter(customer=customer, course=course).exists():
                    skipped_count += 1
                    continue
                print(customer, course, primary_instructor, start_date, price_paid, is_paid,notes)
                # Create enrollment
                enrollment = CourseEnrollment.objects.create(
                    customer=customer,
                    course=course,
                    primary_instructor=primary_instructor,
                    start_date=start_date,
                    price_paid=price_paid,
                    is_paid=is_paid,
                    notes=notes
                )

                # Create course sessions based on template sessions or fallback to default
                template_sessions = CourseSession.objects.filter(template_course=course).order_by('session_number')
                if template_sessions.exists():
                    # Use template sessions
                    for template in template_sessions:
                        CourseSession.objects.create(
                            enrollment=enrollment,
                            session_number=template.session_number,
                            session_type=template.session_type,
                            title=template.title,
                            description=template.description,
                            skills_covered=template.skills_covered
                        )
                else:
                    # Fallback to default sessions if no templates exist
                    for i in range(1, course.total_dives + 1):
                        CourseSession.objects.create(
                            enrollment=enrollment,
                            session_number=i,
                            session_type='OPEN_WATER',
                            title=f'Dive {i}',
                            description=f'Dive session {i} of {course.name}'
                        )

                enrolled_count += 1

            success_msg = f'Successfully enrolled {enrolled_count} customers in {course.name}!'
            if skipped_count > 0:
                success_msg += f' {skipped_count} customers were already enrolled and were skipped.'

            messages.success(request, success_msg)
            return redirect('users:course_enrollments')
        else:
            messages.error(request, 'Please correct the form errors.')
    else:
        form = MultipleCustomerEnrollmentForm(diving_center=request.user)

    # Get available dive schedules for session scheduling
    from datetime import date
    available_dives = DiveSchedule.objects.filter(
        diving_center=request.user,
        date__gte=date.today()
    ).order_by('date', 'time')

    return render(request, 'users/enroll_multiple_customers.html', {
        'form': form,
        'available_dives': available_dives
    })


@login_required
def edit_diving_group(request, group_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    group = get_object_or_404(DivingGroup, id=group_id, diving_center=request.user)

    if request.method == 'POST':
        form = DivingGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diving group updated successfully!')
            return redirect('users:diving_groups_list')
    else:
        form = DivingGroupForm(instance=group)
    return render(request, 'users/edit_diving_group.html', {'form': form, 'group': group})

@login_required
def delete_diving_group(request, group_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    group = get_object_or_404(DivingGroup, id=group_id, diving_center=request.user)

    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Diving group "{group_name}" deleted successfully!')
        return redirect('users:diving_groups_list')

    return render(request, 'users/delete_diving_group.html', {'group': group})

@login_required
def download_medical_form_pdf(request, customer_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    customer = get_object_or_404(Customer, id=customer_id, diving_center=request.user)

    from django.http import HttpResponse
    from django.template.loader import get_template

    # Try to import reportlab for PDF generation
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        import io

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="formulario_medico_{customer.first_name}_{customer.last_name}.pdf"'

        # Create PDF document
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#007bff')
        )

        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#007bff')
        )

        normal_style = styles['Normal']

        # Build PDF content
        content = []

        # Title
        content.append(Paragraph(f"Formulario Médico - {customer.get_full_name()}", title_style))
        content.append(Spacer(1, 20))

        # Personal Information
        content.append(Paragraph("Información Personal", section_style))
        personal_info = f"""
        <b>Nombre:</b> {customer.first_name} {customer.last_name}<br/>
        <b>Email:</b> {customer.email}<br/>
        <b>Teléfono:</b> {customer.phone_number or 'No proporcionado'}<br/>
        <b>País:</b> {customer.get_country_display() or 'No especificado'}<br/>
        <b>Idioma:</b> {customer.get_language_display()}<br/>
        <b>Fecha de nacimiento:</b> {customer.birthday or 'No proporcionada'}<br/>
        <b>Edad:</b> {f'{customer.get_age()} años' if customer.get_age() else 'No calculado'}<br/>
        <b>Nivel de certificación:</b> {customer.get_certification_level_display()}
        """
        content.append(Paragraph(personal_info, normal_style))
        content.append(Spacer(1, 20))

        # Physical Information
        content.append(Paragraph("Información Física", section_style))
        physical_info = f"""
        <b>Peso:</b> {customer.weight or 'No proporcionado'} kg<br/>
        <b>Altura:</b> {customer.height or 'No proporcionada'} cm<br/>
        <b>Talla de pie:</b> {customer.foot_size or 'No proporcionada'} EU<br/>
        <b>Talla de traje:</b> {customer.get_wetsuit_size()}<br/>
        <b>Talla de jacket:</b> {customer.get_bcd_size()}<br/>
        <b>Talla de aletas:</b> {customer.get_fins_size()}
        """
        if customer.swimming_ability:
            physical_info += f"<br/><b>Habilidad para nadar:</b> {customer.get_swimming_ability_display()}"
        content.append(Paragraph(physical_info, normal_style))
        content.append(Spacer(1, 20))

        # Emergency Contact
        if customer.emergency_contact:
            content.append(Paragraph("Contacto de Emergencia", section_style))
            content.append(Paragraph(customer.emergency_contact, normal_style))
            content.append(Spacer(1, 20))

        # Medical Questionnaire
        if customer.medical_questionnaire_answers:
            content.append(Paragraph("Cuestionario Médico", section_style))

            questions_text = {
                'pregunta_1': '¿Ha tenido problemas con los pulmones/respiración, corazón o sangre?',
                'pregunta_1_1': 'Cirugía de pecho, corazón, válvulas cardíacas, dispositivos cardiovasculares implantables, neumotórax',
                'pregunta_1_2': 'Asma, sibilancias, alergias severas en los últimos 12 meses',
                'pregunta_1_3': 'Problemas de función pulmonar o enfermedad torácica',
                'pregunta_1_4': 'Presión arterial alta o medicación para controlarla',
                'pregunta_2': '¿Ha tenido problemas con el cerebro o sistema nervioso?',
                'pregunta_2_1': 'Problemas de salud mental o psicológicos que requieren medicación',
                'pregunta_2_2': 'Lesión en la cabeza en los últimos 12 meses',
                'pregunta_2_3': 'Problemas persistentes de equilibrio, mareos, desmayos, convulsiones',
                'pregunta_2_4': 'Incapacidad para realizar ejercicio moderadamente intenso',
                'pregunta_3': '¿Está tomando medicamentos o está embarazada?',
                'pregunta_3_1': 'Medicamentos de prescripción (excepto anticonceptivos o antimaláricos)',
                'pregunta_3_2': 'Embarazo o posible embarazo',
                'pregunta_4': '¿Ha tenido que obtener autorización médica para bucear?',
                'pregunta_5': '¿Es mayor de 45 años y tiene alguna condición específica?',
                'pregunta_5_1': 'Fuma o inhala nicotina regularmente',
                'pregunta_5_2': 'Alto nivel de colesterol',
                'pregunta_5_3': 'Historial familiar de ataques cardíacos o derrames cerebrales',
                'pregunta_5_4': 'Diabetes mellitus actualmente tratada con medicación',
            }

            for key, question in questions_text.items():
                if key in customer.medical_questionnaire_answers:
                    answer = 'SÍ' if customer.medical_questionnaire_answers[key] == '1' else 'NO'
                    color = 'red' if answer == 'SÍ' else 'green'
                    content.append(Paragraph(f"<b>{question}</b><br/><font color='{color}'><b>{answer}</b></font>", normal_style))
                    content.append(Spacer(1, 10))

        # Additional Medical Information
        if customer.medical_conditions:
            content.append(Paragraph("Información Médica Adicional", section_style))
            content.append(Paragraph(customer.medical_conditions, normal_style))
            content.append(Spacer(1, 20))

        # Creation date
        content.append(Paragraph(f"<b>Formulario completado el:</b> {customer.created_at.strftime('%d/%m/%Y %H:%M')}", normal_style))

        # Build PDF```python
        doc.build(content)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    except ImportError:
        # Fallback if reportlab is not installed
        messages.error(request, 'PDF generation library not available. Please contact administrator.')
        return redirect('users:customer_medical_detail', customer_id=customer.id)


@login_required
def generate_qr_code(request, dive_center_uuid=None):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Acceso denegado.')
        return redirect('users:profile')

    # Use the current user's UUID if not specified
    if not dive_center_uuid:
        dive_center_uuid = request.user.userprofile.uuid

    # Generate the full URL for the medical form
    medical_form_url = request.build_absolute_uri(
        reverse('users:medical_form_with_uuid', kwargs={'dive_center_uuid': dive_center_uuid})
    )

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(medical_form_url)
    qr.make(fit=True)

    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)

    # Return as downloadable file
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_formulario_alta_{request.user.userprofile.business_name or request.user.username}.png"'

    return response


@login_required
def get_medical_form_url(request):
    print(111)
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'error': 'Access denied'}, status=403)

    medical_form_url = request.build_absolute_uri(
        reverse('users:medical_form_with_uuid', kwargs={'dive_center_uuid': request.user.userprofile.uuid})
    )

    print(medical_form_url)

    return JsonResponse({'url': medical_form_url})

@login_required
def schedule_multiple_sessions(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = ScheduleMultipleSessionsForm(diving_center=request.user, data=request.POST)

        # Get the course and session number from the form data to set the proper queryset
        course_id = request.POST.get('course')
        session_number = request.POST.get('session_number')

        if course_id:
            try:
                course = Course.objects.get(id=course_id, diving_center=request.user)
                pending_sessions = CourseSession.objects.filter(
                    enrollment__course=course,
                    status='NOT_SCHEDULED'
                ).select_related('enrollment__customer')

                if session_number:
                    pending_sessions = pending_sessions.filter(session_number=session_number)

                # Update the form's sessions queryset with the actual pending sessions
                form.fields['sessions'].queryset = pending_sessions

            except Course.DoesNotExist:
                pass

        if form.is_valid():
            dive_schedule = form.cleaned_data['dive_schedule']
            sessions = form.cleaned_data['sessions']
            instructor = form.cleaned_data.get('instructor')

            scheduled_count = 0

            for session in sessions:
                # Update session details
                session.dive_schedule = dive_schedule
                session.scheduled_date = dive_schedule.date
                session.scheduled_time = dive_schedule.time
                if instructor:
                    session.instructor = instructor
                session.status = 'SCHEDULED'
                session.save()

                # Create CustomerDiveActivity for this course session
                defaults = {
                    'course': session.enrollment.course,
                    'course_session': session,
                    'assigned_staff': instructor,
                    'tank_size': session.enrollment.customer.default_tank_size,
                }

                # Auto-set equipment needs if course includes material
                if session.enrollment.course.includes_material:
                    defaults.update({
                        'needs_wetsuit': True,
                        'needs_bcd': True,
                        'needs_regulator': True,
                    })

                customer_dive_activity, created = CustomerDiveActivity.objects.get_or_create(
                    customer=session.enrollment.customer,
                    dive_schedule=dive_schedule,
                    defaults=defaults
                )

                if not created:
                    customer_dive_activity.course = session.enrollment.course
                    customer_dive_activity.course_session = session
                    if instructor:
                        customer_dive_activity.assigned_staff = instructor

                    if session.enrollment.course.includes_material:
                        customer_dive_activity.needs_wetsuit = True
                        customer_dive_activity.needs_bcd = True
                        customer_dive_activity.needs_regulator = True

                    customer_dive_activity.save()

                # Update enrollment status if needed
                session.enrollment.auto_update_status()
                scheduled_count += 1

            messages.success(request, f'¡{scheduled_count} sesiones programadas exitosamente!')
            return redirect('users:schedule_multiple_sessions')
        else:
            print(form.errors)
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = ScheduleMultipleSessionsForm(diving_center=request.user)

    return render(request, 'users/schedule_multiple_sessions.html', {
        'form': form
    })

@login_required
def get_pending_sessions(request):
    """AJAX endpoint to get pending sessions for a course and session number"""
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'error': 'Access denied'}, status=403)

    course_id = request.GET.get('course_id')
    session_number = request.GET.get('session_number')

    if not course_id:
        return JsonResponse({'sessions': []})

    try:
        course = Course.objects.get(id=course_id, diving_center=request.user)

        # Get pending sessions for this course
        pending_sessions = CourseSession.objects.filter(
            enrollment__course=course,
            status='NOT_SCHEDULED'
        ).select_related('enrollment__customer')

        if session_number:
            pending_sessions = pending_sessions.filter(session_number=session_number)

        sessions_data = []
        for session in pending_sessions:
            sessions_data.append({
                'id': session.id,
                'session_number': session.session_number,
                'title': session.title,
                'customer_name': session.enrollment.customer.get_full_name(),
                'enrollment_id': session.enrollment.id
            })

        return JsonResponse({'sessions': sessions_data})

    except Course.DoesNotExist:
        return JsonResponse({'error': 'Course not found'}, status=404)

@login_required
def get_course_sessions(request, course_id):
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        course = Course.objects.get(id=course_id, diving_center=request.user)

        # Get template sessions for this course
        template_sessions = CourseSession.objects.filter(
            template_course=course
        ).order_by('session_number')

        sessions_data = []
        if template_sessions.exists():
            for session in template_sessions:
                sessions_data.append({
                    'session_number': session.session_number,
                    'title': session.title,
                    'session_type': session.get_session_type_display(),
                    'description': session.description,
                    'skills_covered': session.skills_covered
                })
        else:
            # If no template sessions, create default ones based on total_dives
            for i in range(1, course.total_dives + 1):
                sessions_data.append({
                    'session_number': i,
                    'title': f'Inmersión {i}',
                    'session_type': 'Aguas Abiertas',
                    'description': f'Sesión de inmersión {i} de {course.name}',
                    'skills_covered': ''
                })

        return JsonResponse({
            'course_name': course.name,
            'total_dives': course.total_dives,
            'sessions': sessions_data
        })

    except Course.DoesNotExist:
        return JsonResponse({'error': 'Course not found'}, status=404)

@login_required
def ajax_search_dives(request):
    """AJAX endpoint to search for available dives"""
    if not request.user.userprofile.is_diving_center:
        return JsonResponse({'error': 'Access denied'}, status=403)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    group_size = request.GET.get('group_size', 1)

    try:
        group_size = int(group_size)
    except (ValueError, TypeError):
        group_size = 1

    if not start_date or not end_date:
        return JsonResponse({'error': 'Start date and end date are required'}, status=400)

    try:
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    # Get dives in the specified date range
    dives = DiveSchedule.objects.filter(
        diving_center=request.user,
        date__gte=start_date_obj,
        date__lte=end_date_obj
    ).select_related('dive_site').order_by('date', 'time')

    dives_data = []
    for dive in dives:
        participant_count = dive.get_participant_count()
        available_spots = dive.get_available_spots()
        
        dives_data.append({
            'id': dive.id,
            'date': dive.date.strftime('%Y-%m-%d'),
            'time': dive.time.strftime('%H:%M'),
            'dive_site_name': dive.dive_site.name,
            'description': dive.description,
            'participant_count': participant_count,
            'max_participants': dive.max_participants,
            'available_spots': available_spots,
            'can_accommodate_group': available_spots >= group_size,
            'special_notes': dive.special_notes
        })

    return JsonResponse({'dives': dives_data})