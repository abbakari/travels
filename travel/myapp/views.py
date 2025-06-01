from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q  # Added import for Q
from .models import Destination, Package, Booking, Contact
from .forms import ContactForm, BookingForm, PackageForm, DestinationForm, EditProfileForm, CustomUserCreationForm, CustomAuthenticationForm  # Added DestinationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import update_session_auth_hash

# Utility functions
def is_admin(user):
    return user.is_staff

# Set default admin (if not exists)
def set_default_admin():
    User = get_user_model()
    admin_username = 'admin'
    admin_email = 'admin@example.com'
    admin_password = 'admin12345'  # Change this after first login for security!
    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(admin_username, admin_email, admin_password)

# Call this function at startup (optional, e.g. in ready() of apps.py or manually)
# set_default_admin()

# Public Views
def home_view(request):
    featured_destinations = Destination.objects.all().order_by('-created_at')[:3]
    return render(request, 'myapp/index.html', {'featured_destinations': featured_destinations})

def packages_view(request):
    packages_list = Package.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(packages_list, 6)  # Show 6 packages per page
    page_number = request.GET.get('page')
    packages = paginator.get_page(page_number)

    return render(request, 'myapp/packages.html', {'packages': packages})

@login_required
def create_booking_view(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        package = get_object_or_404(Package, id=package_id)
        
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.package = package
            booking.save()
            messages.success(request, 'Your booking has been created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('packages')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'myapp/contact.html', {'form': form})

# Authentication Views
def register_view(request):
    set_default_admin()  # Ensure default admin exists on registration page access
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'myapp/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm(request)
    return render(request, 'myapp/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

# Dashboard Views
@login_required
def dashboard_view(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'myapp/dashboard.html', {'bookings': user_bookings})

# Admin Views
@staff_member_required
def admin_dashboard_view(request):
    total_packages = Package.objects.count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    recent_bookings = Booking.objects.order_by('-booking_date')[:5]
    
    context = {
        'total_packages': total_packages,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'myapp/admin/dashboard.html', context)

@staff_member_required
def manage_bookings_view(request):
    bookings_list = Booking.objects.all().order_by('-booking_date')
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        bookings_list = bookings_list.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        bookings_list = bookings_list.filter(
            Q(user__username__icontains=search_query) |
            Q(package__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bookings_list, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    return render(request, 'myapp/admin/manage_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'search_query': search_query or '',
    })

@staff_member_required
def manage_packages_view(request):
    packages_list = Package.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        packages_list = packages_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )  # Fixed missing parenthesis
    
    # Pagination
    paginator = Paginator(packages_list, 10)
    page_number = request.GET.get('page')
    packages = paginator.get_page(page_number)
    
    return render(request, 'myapp/admin/manage_packages.html', {
        'packages': packages,
        'search_query': search_query or '',
    })

@staff_member_required
def add_package_view(request):
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            messages.success(request, 'Package added successfully!')
            return redirect('manage_packages')
    else:
        form = PackageForm()
    
    return render(request, 'myapp/admin/package_form.html', {
        'form': form,
        'title': 'Add New Package'
    })

@staff_member_required
def edit_package_view(request, pk):
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package updated successfully!')
            return redirect('manage_packages')
    else:
        form = PackageForm(instance=package)
    
    return render(request, 'myapp/admin/package_form.html', {
        'form': form,
        'title': 'Edit Package'
    })

@staff_member_required
def delete_package_view(request, pk):
    package = get_object_or_404(Package, pk=pk)
    package.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, 'Package deleted successfully!')
    return redirect('manage_packages')

@staff_member_required
def update_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('manage_bookings')
    else:
        form = BookingForm(instance=booking)
    
    return render(request, 'myapp/admin/booking_form.html', {
        'form': form,
        'booking': booking
    })

@csrf_exempt
@require_POST
@staff_member_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Booking.STATUS_CHOICES).keys():
        booking.status = new_status
        booking.save()
        return JsonResponse({'success': True, 'new_status': booking.get_status_display()})
    
    return JsonResponse({'success': False, 'error': 'Invalid status'})

# Destination Management Views
@staff_member_required
def manage_destinations_view(request):
    destinations_list = Destination.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        destinations_list = destinations_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query))
    
    # Pagination
    paginator = Paginator(destinations_list, 10)
    page_number = request.GET.get('page')
    destinations = paginator.get_page(page_number)
    
    return render(request, 'myapp/admin/manage_destinations.html', {
        'destinations': destinations,
        'search_query': search_query or '',
    })

@staff_member_required
def add_destination_view(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            destination = form.save()
            messages.success(request, 'Destination added successfully!')
            return redirect('manage_destinations')
    else:
        form = DestinationForm()
    
    return render(request, 'myapp/admin/destination_form.html', {
        'form': form,
        'title': 'Add New Destination'
    })

@staff_member_required
def edit_destination_view(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination updated successfully!')
            return redirect('manage_destinations')
    else:
        form = DestinationForm(instance=destination)

    return render(request, 'myapp/admin/destination_form.html', {
        'form': form,
        'title': 'Edit Destination'
    })

@staff_member_required
def delete_destination_view(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.delete()
        messages.success(request, 'Destination deleted successfully!')
        return redirect('manage_destinations')
    
    return render(request, 'myapp/admin/confirm_delete.html', {
        'object': destination,
        'type': 'destination'
    })

from django.views.decorators.http import require_POST

@login_required
def cancel_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Your booking has been cancelled.')
        return redirect('dashboard')
    return render(request, 'myapp/confirm_delete.html', {
        'object': booking,
        'type': 'booking'
    })

@staff_member_required
@require_POST
def delete_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.delete()
    messages.success(request, 'Booking deleted successfully!')
    return redirect('manage_bookings')

@login_required
def view_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'myapp/booking_detail.html', {'booking': booking})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'myapp/edit_profile.html', {'form': form})