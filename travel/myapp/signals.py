from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

@receiver(post_save, sender=Booking)
def send_booking_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'Your Booking Confirmation'
        message = f'''
        Dear {instance.user.username},
        
        Thank you for booking {instance.package.name} with TravelEase!
        
        Booking Details:
        - Package: {instance.package.name}
        - Travel Date: {instance.travel_date}
        - Guests: {instance.guests}
        - Status: {instance.get_status_display()}
        
        We'll contact you soon with more details about your trip.
        
        Best regards,
        TravelEase Team
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=False,
        )