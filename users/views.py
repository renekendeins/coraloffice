from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
import calendar
from .forms import SignUpForm, UserForm, UserProfileForm, CustomerForm, DiveScheduleForm, DiveActivityForm, CustomerDiveActivityForm
from .models import UserProfile, Customer, DiveSchedule, DiveActivity, CustomerDiveActivity


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

    customers = Customer.objects.filter(diving_center=request.user)
    recent_dives = DiveSchedule.objects.filter(
        diving_center=request.user).order_by('-date')[:5]

    return render(request, 'users/diving_center_dashboard.html', {
        'customers': customers,
        'recent_dives': recent_dives
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
        form = DiveScheduleForm(request.POST)
        if form.is_valid():
            dive = form.save(commit=False)
            dive.diving_center = request.user
            dive.save()
            messages.success(request, 'Dive scheduled successfully!')
            return redirect('users:dive_calendar')
    else:
        form = DiveScheduleForm()
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
        dives_by_day[day].append(dive)

    # Navigation dates
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    context = {
        'calendar':
        cal,
        'month_name':
        month_name,
        'year':
        year,
        'month':
        month,
        'dives_by_day':
        dives_by_day,
        'prev_month':
        prev_month,
        'prev_year':
        prev_year,
        'next_month':
        next_month,
        'next_year':
        next_year,
        'today':
        today.day if year == today.year and month == today.month else None,
    }

    return render(request, 'users/calendar_view.html', context)


@login_required
def quick_schedule_dive(request):
    if not request.user.userprofile.is_diving_center:
        messages.error(request, 'Access denied.')
        return redirect('users:profile')

    selected_date = request.GET.get('date')

    if request.method == 'POST':
        form = DiveScheduleForm(request.POST)
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
        form = DiveScheduleForm(initial=initial_data)

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
        
        # Handle adding a participant
        form = CustomerDiveActivityForm(request.user, request.POST)
        print("mmmm" + request.POST.get('customer'))
        if form.is_valid():
            
            participant = form.save(commit=False)
            participant.dive_schedule = dive
            participant.save()
            messages.success(request, 'Participant added to dive!')
            return 
            redirect('users:manage_dive_participants', dive_id=dive.id)
    else:
        form = CustomerDiveActivityForm(request.user)

    # Logic to handle participant removal
    if request.method == 'POST' and 'remove_participant' in request.POST:
        
        participant_id = request.POST.get(
            'customer')  # Get the participant_id from the POST data
        if participant_id:  # Ensure it's not empty
            participant = get_object_or_404(
                CustomerDiveActivity,
                id=int(participant_id))  # Convert ID to int
            participant.delete()
            messages.success(request, 'Participant removed from the dive!')
            return redirect('users:manage_dive_participants', dive_id=dive.id)

    return render(request, 'users/manage_dive_participants.html', {
        'dive': dive,
        'participants': participants,
        'form': form
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

    if request.method == 'POST':
        # Handle updating the dive details logic here if needed
        # Example (pseudo-code to update dive details):
        # Could be handled via a form, similar to adding or updating dives
        pass

    return render(request, 'users/dive_detail.html', {
        'dive': dive,
        'participants': participants
    })
