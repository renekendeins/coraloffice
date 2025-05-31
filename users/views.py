from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
import calendar
from .forms import SignUpForm, UserForm, UserProfileForm, CustomerForm, DiveScheduleForm, DiveActivityForm, CustomerDiveActivityForm, DivingSiteForm, InventoryItemForm, DivingGroupForm, MedicalForm
from .models import UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity, DivingSite, InventoryItem, DivingGroup, DivingGroupMember


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


def user_list(request):
    users = User.objects.select_related('userprofile').all()
    return render(request, 'users/user_list.html', {'users': users})


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

    customers = Customer.objects.filter(diving_center=request.user)
    return render(request, 'users/customer_list.html',
                  {'customers': customers})


@login_required
def add_customer(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.diving_center = request.user
            customer.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('users:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'users/add_customer.html', {'form': form})


@login_required
def dive_calendar(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    dives = DiveSchedule.objects.filter(diving_center=request.user).order_by(
        'date', 'time')
    return render(request, 'users/dive_calendar.html', {'dives': dives})


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
            return redirect('users:dive_calendar')
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
        form = CustomerForm(request.POST, instance=customer)
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
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    # Get current month and year or from query params
    today = datetime.now()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    view_type = request.GET.get('view', 'month')  # month, week, day

    if view_type == 'day':
        # Day view - show specific day
        selected_date = datetime(year, month, int(request.GET.get('day', today.day)))
        dives = DiveSchedule.objects.filter(
            diving_center=request.user,
            date=selected_date.date()
        ).order_by('time')
        
        # Add participant count to dive objects
        for dive in dives:
            dive.participant_count = dive.get_participant_count()
            
        context = {
            'view_type': view_type,
            'selected_date': selected_date,
            'dives': dives,
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
        }
        
    elif view_type == 'week':
        # Week view - show week containing the selected day
        selected_date = datetime(year, month, int(request.GET.get('day', today.day)))
        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        dives = DiveSchedule.objects.filter(
            diving_center=request.user,
            date__range=[week_start.date(), week_end.date()]
        ).order_by('date', 'time')
        
        # Organize dives by day for the week
        week_dives = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            week_dives[day.date()] = []
            
        for dive in dives:
            dive.participant_count = dive.get_participant_count()
            week_dives[dive.date].append(dive)
            
        context = {
            'view_type': view_type,
            'week_start': week_start,
            'week_end': week_end,
            'week_dives': week_dives,
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
        }
        
    else:  # month view (default)
        # Create calendar
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]

        # Get all dives for this month
        dives = DiveSchedule.objects.filter(diving_center=request.user,
                                            date__year=year,
                                            date__month=month)

        # Organize dives by day
        dives_by_day = {}
        for dive in dives:
            day = dive.date.day
            if day not in dives_by_day:
                dives_by_day[day] = []
            # Add participant count to dive object
            dive.participant_count = dive.get_participant_count()
            dives_by_day[day].append(dive)
            
        context = {
            'view_type': view_type,
            'calendar': cal,
            'month_name': month_name,
            'year': year,
            'month': month,
            'dives_by_day': dives_by_day,
            'today': today.day if year == today.year and month == today.month else None,
        }

    # Navigation dates
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    # Navigation dates (common for all views)
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    # Add navigation to context
    context.update({
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })

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
                messages.success(request, f'{participant.customer} is now on board!')
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
                participant.tank_size = request.POST.get('tank_size', participant.tank_size)
                participant.status = request.POST.get('status', participant.status)
                participant.needs_wetsuit = 'needs_wetsuit' in request.POST
                participant.needs_bcd = 'needs_bcd' in request.POST
                participant.needs_regulator = 'needs_regulator' in request.POST
                participant.needs_guide = 'needs_guide' in request.POST
                participant.needs_insurance = 'needs_insurance' in request.POST
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
                    # Add all group members
                    group_members = DivingGroupMember.objects.filter(group=selected_group)
                    added_count = 0
                    for member in group_members:
                        # Check if member not already participating
                        if not CustomerDiveActivity.objects.filter(dive_schedule=dive, customer=member.customer).exists():
                            CustomerDiveActivity.objects.create(
                                customer=member.customer,
                                dive_schedule=dive,
                                activity=form.cleaned_data['activity'],
                                tank_size=form.cleaned_data['tank_size'],
                                needs_wetsuit=form.cleaned_data['needs_wetsuit'],
                                needs_bcd=form.cleaned_data['needs_bcd'],
                                needs_regulator=form.cleaned_data['needs_regulator'],
                                needs_guide=form.cleaned_data['needs_guide'],
                                needs_insurance=form.cleaned_data['needs_insurance'],
                            )
                            added_count += 1
                    messages.success(request, f'Added {added_count} group members to dive!')
                else:
                    # Add single participant
                    participant = form.save(commit=False)
                    participant.dive_schedule = dive
                    participant.save()
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
            messages.success(request, 'Customer added to the dive!')
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

    # Calculate equipment counts
    equipment_counts = {
        'wetsuits': participants.filter(needs_wetsuit=True).count(),
        'bcds': participants.filter(needs_bcd=True).count(),
        'regulators': participants.filter(needs_regulator=True).count(),
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
    from datetime import date
    import json

    customers = Customer.objects.filter(diving_center=request.user)
    activities = CustomerDiveActivity.objects.filter(
        customer__diving_center=request.user
    )

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

    # Activities by date
    activities_by_date = activities.values(
        'dive_schedule__date'
    ).annotate(
        count=Count('id')
    ).order_by('dive_schedule__date')

    # Prepare data for charts
    date_labels = [item['dive_schedule__date'].strftime('%Y-%m-%d') for item in activities_by_date]
    date_counts = [item['count'] for item in activities_by_date]

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
    
    groups = DivingGroup.objects.filter(diving_center=request.user)
    return render(request, 'users/diving_groups_list.html', {'groups': groups})


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
    members = DivingGroupMember.objects.filter(group=group)
    available_customers = Customer.objects.filter(diving_center=request.user).exclude(
        id__in=members.values_list('customer_id', flat=True)
    )
    
    # Get available dives for scheduling
    from datetime import date
    available_dives = DiveSchedule.objects.filter(
        diving_center=request.user,
        date__gte=date.today()
    ).order_by('date', 'time')

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
        
        elif 'schedule_group' in request.POST:
            dive_ids = request.POST.getlist('selected_dives')
            activity_id = request.POST.get('activity_id')
            tank_size = request.POST.get('tank_size', '12L')
            needs_wetsuit = 'needs_wetsuit' in request.POST
            needs_bcd = 'needs_bcd' in request.POST
            needs_regulator = 'needs_regulator' in request.POST
            needs_guide = 'needs_guide' in request.POST
            needs_insurance = 'needs_insurance' in request.POST
            
            if dive_ids and activity_id:
                activity = get_object_or_404(DiveActivity, id=activity_id, diving_center=request.user)
                scheduled_count = 0
                
                for dive_id in dive_ids:
                    dive = get_object_or_404(DiveSchedule, id=dive_id, diving_center=request.user)
                    
                    # Add all group members to this dive
                    for member in members:
                        # Check if member not already in this dive
                        if not CustomerDiveActivity.objects.filter(
                            dive_schedule=dive, 
                            customer=member.customer
                        ).exists():
                            CustomerDiveActivity.objects.create(
                                customer=member.customer,
                                dive_schedule=dive,
                                activity=activity,
                                tank_size=tank_size,
                                needs_wetsuit=needs_wetsuit,
                                needs_bcd=needs_bcd,
                                needs_regulator=needs_regulator,
                                needs_guide=needs_guide,
                                needs_insurance=needs_insurance,
                            )
                            scheduled_count += 1
                
                messages.success(request, f'Successfully scheduled {group.name} for {len(dive_ids)} dive(s)! Added {scheduled_count} participant slots.')
                return redirect('users:manage_group_members', group_id=group.id)
            else:
                messages.error(request, 'Please select at least one dive and an activity.')

    # Get group activities and tank size choices for the form
    group_activities = DiveActivity.objects.filter(diving_center=request.user)
    tank_choices = CustomerDiveActivity.TANK_SIZE_CHOICES

    return render(request, 'users/manage_group_members.html', {
        'group': group,
        'members': members,
        'available_customers': available_customers,
        'available_dives': available_dives,
        'group_activities': group_activities,
        'tank_choices': tank_choices,
    })


# Edit and Delete Dive Views
@login_required
def edit_dive(request, dive_id):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    dive = get_object_or_404(DiveSchedule, id=dive_id, diving_center=request.user)

    if request.method == 'POST':
        form = DiveScheduleForm(request.POST, instance=dive)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dive updated successfully!')
            return redirect('users:dive_detail', dive_id=dive.id)
    else:
        form = DiveScheduleForm(instance=dive)
    
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
        return redirect('users:dive_calendar')

    return render(request, 'users/delete_dive.html', {'dive': dive})


@login_required
def medical_forms_list(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')
    
    medical_forms = Customer.objects.filter(diving_center=request.user).order_by('-created_at')
    return render(request, 'users/medical_forms_list.html', {'medical_forms': medical_forms})


# Medical Form (accessible without login)
def medical_form(request):
    if request.method == 'POST':
        form = MedicalForm(request.POST)
        if form.is_valid():
            # Create customer but assign to first diving center found
            # In a real app, you'd want to handle this differently
            diving_center = User.objects.filter(userprofile__is_diving_center=True).first()
            if diving_center:
                customer = form.save(commit=False)
                customer.diving_center = diving_center
                customer.save()
                messages.success(request, 'Medical form submitted successfully! A diving center will contact you soon.')
                return redirect('users:medical_form')
            else:
                messages.error(request, 'No diving center available. Please contact us directly.')
    else:
        form = MedicalForm()
    
    return render(request, 'users/medical_form.html', {'form': form})
