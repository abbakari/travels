from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.home_view, name='home'),
    path('packages/', views.packages_view, name='packages'),
    path('book/', views.create_booking_view, name='create_booking'),
    path('contact/', views.contact_view, name='contact'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/bookings/', views.manage_bookings_view, name='manage_bookings'),
    path('admin/bookings/update/<int:pk>/', views.update_booking_view, name='update_booking'),
    path('admin/bookings/update-status/<int:pk>/', views.update_booking_status, name='update_booking_status'),
    
    path('admin/packages/', views.manage_packages_view, name='manage_packages'),
    path('admin/packages/add/', views.add_package_view, name='add_package'),
    path('admin/packages/edit/<int:pk>/', views.edit_package_view, name='edit_package'),
    path('admin/packages/delete/<int:pk>/', views.delete_package_view, name='delete_package'),
    
    path('admin/destinations/', views.manage_destinations_view, name='manage_destinations'),
    path('admin/destinations/add/', views.add_destination_view, name='add_destination'),
    path('admin/destinations/edit/<int:pk>/', views.edit_destination_view, name='edit_destination'),
    path('admin/destinations/delete/<int:pk>/', views.delete_destination_view, name='delete_destination'),
    
    # Booking management URLs
    path('bookings/cancel/<int:pk>/', views.cancel_booking_view, name='cancel_booking'),
    path('admin/bookings/delete/<int:pk>/', views.delete_booking_view, name='delete_booking'),
    path('bookings/view/<int:pk>/', views.view_booking_view, name='view_booking'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
]