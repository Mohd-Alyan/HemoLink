from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from accounts.models import CustomUser, DonorProfile
from donations.models import BloodBank, BloodRequest, Notification, Pledge, DonationHistory

# Blood type compatibility map: who can donate to whom
COMPATIBLE_DONORS = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-'],
}


def home(request):
    return render(request, 'app1/home.html')


def login_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')

        elif form_type == 'register':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            user_type = request.POST.get('user_type')
            phone_number = request.POST.get('phone_number', '')
            blood_group = request.POST.get('blood_group', '')

            if password == confirm_password:
                if CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'Username already taken.')
                else:
                    user = CustomUser.objects.create_user(
                        username=username, email=email, password=password,
                        user_type=user_type, phone_number=phone_number,
                    )
                    if user_type == 'donor':
                        DonorProfile.objects.create(
                            user=user,
                            blood_group=blood_group if blood_group else 'N/A',
                        )
                    auth_login(request, user)
                    return redirect('dashboard')
            else:
                messages.error(request, 'Passwords do not match.')

    return render(request, 'app1/login.html')


@login_required(login_url='login')
def donor_dashboard(request):
    user = request.user

    # Donor-specific context
    donor_profile = None
    donation_history = []
    try:
        donor_profile = user.donor_profile
        donation_history = DonationHistory.objects.filter(donor=user).order_by('-donated_at')[:10]
    except DonorProfile.DoesNotExist:
        pass

    # Hospital/patient: show their own requests + incoming pledges
    my_requests = BloodRequest.objects.filter(requested_by=user).order_by('-created_at')[:10]

    return render(request, 'app1/dashboard.html', {
        'donor_profile': donor_profile,
        'donation_history': donation_history,
        'my_requests': my_requests,
    })


@login_required(login_url='login')
def edit_profile(request):
    user = request.user
    try:
        profile = user.donor_profile
    except DonorProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', '')
        user.save()

        if profile:
            profile.blood_group = request.POST.get('blood_group', profile.blood_group)
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat:
                profile.latitude = lat
            if lng:
                profile.longitude = lng
            profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard')

    return render(request, 'app1/edit_profile.html', {'donor_profile': profile})


@login_required(login_url='login')
def active_requests(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        blood_group_required = request.POST.get('blood_group_required')
        units_required = request.POST.get('units_required')
        location = request.POST.get('location')
        urgency_level = request.POST.get('urgency_level')

        blood_request = BloodRequest.objects.create(
            requested_by=request.user,
            patient_name=patient_name,
            blood_group_required=blood_group_required,
            units_required=units_required,
            location=location,
            urgency_level=urgency_level,
            status='pending'
        )

        # Auto-alert compatible available donors
        compatible_groups = COMPATIBLE_DONORS.get(blood_group_required, [])
        matching_donors = DonorProfile.objects.filter(
            is_available=True,
            blood_group__in=compatible_groups,
        ).exclude(user=request.user).select_related('user')

        for dp in matching_donors:
            Notification.objects.create(
                user=dp.user,
                message=f"🚨 Emergency: {blood_group_required} blood needed for {patient_name} at {location}. Urgency: {urgency_level.upper()}. You are a compatible donor!",
                related_request=blood_request,
            )

        alert_count = matching_donors.count()
        messages.success(request, f'Blood request broadcasted successfully. {alert_count} compatible donor(s) notified.')
        return redirect('requests')

    all_requests = BloodRequest.objects.filter(status='pending').order_by('-created_at')
    user_pledged_ids = set(
        Pledge.objects.filter(donor=request.user).values_list('blood_request_id', flat=True)
    )

    return render(request, 'app1/request.html', {
        'active_requests': all_requests,
        'user_pledged_ids': user_pledged_ids,
    })


@login_required(login_url='login')
@require_POST
def pledge_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    _, created = Pledge.objects.get_or_create(donor=request.user, blood_request=blood_request)
    if created:
        Notification.objects.create(
            user=blood_request.requested_by,
            message=f"{request.user.username} has pledged to donate {blood_request.blood_group_required} blood for {blood_request.patient_name}.",
            related_request=blood_request,
        )
        messages.success(request, 'You have pledged to this request.')
    else:
        messages.info(request, 'You have already pledged to this request.')
    return redirect('requests')


@login_required(login_url='login')
@require_POST
def fulfill_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id, requested_by=request.user)
    blood_request.status = 'fulfilled'
    blood_request.save()

    # Record donation history for all donors who pledged
    pledges = Pledge.objects.filter(blood_request=blood_request).select_related('donor')
    for pledge in pledges:
        DonationHistory.objects.create(
            donor=pledge.donor,
            blood_request=blood_request,
            blood_group=blood_request.blood_group_required,
            units_donated=1,
            location=blood_request.location,
        )
        # Update donor's last_donation_date
        try:
            profile = pledge.donor.donor_profile
            from django.utils import timezone
            profile.last_donation_date = timezone.now().date()
            profile.save()
        except DonorProfile.DoesNotExist:
            pass

        Notification.objects.create(
            user=pledge.donor,
            message=f"Thank you! The blood request for {blood_request.patient_name} has been fulfilled. Your donation has been recorded.",
            related_request=blood_request,
        )

    messages.success(request, 'Request marked as fulfilled. All pledging donors have been notified.')
    return redirect('requests')


@login_required(login_url='login')
@require_POST
def toggle_availability(request):
    try:
        profile = request.user.donor_profile
        profile.is_available = not profile.is_available
        profile.save()
        return JsonResponse({'status': 'ok', 'is_available': profile.is_available})
    except DonorProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No donor profile found.'}, status=400)


@login_required(login_url='login')
def blood_banks(request):
    banks = BloodBank.objects.all()
    return render(request, 'app1/blood_banks.html', {'blood_banks': banks})


@login_required(login_url='login')
def notifications_status(request):
    tab = request.GET.get('tab', 'all')
    user_notifications = Notification.objects.filter(user=request.user)

    if tab == 'unread':
        user_notifications = user_notifications.filter(is_read=False)
    elif tab == 'sent':
        user_notifications = user_notifications.filter(
            related_request__requested_by=request.user
        )

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    user_notifications = user_notifications.order_by('-created_at')

    if tab != 'unread':
        user_notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'app1/status.html', {
        'notifications': user_notifications,
        'current_tab': tab,
        'unread_count': unread_count,
    })


def logout_view(request):
    auth_logout(request)
    return redirect('home')
