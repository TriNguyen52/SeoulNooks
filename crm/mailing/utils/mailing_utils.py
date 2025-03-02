from django.core.mail import send_mail
from django.conf import settings

def send_application_confirmation(application):
    """Send a confirmation email to the applicant."""
    print(f"📩 Sending confirmation email to {application.email}")  # Debug print
    send_mail(
        subject="Application Received",
        message=f"Dear {application.first_name},\n\n"
                "Thank you for applying! We have received your application.\n"
                "We will review it and get back to you shortly.\n\n"
                "Best regards,\nYour Team",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[application.email],
        fail_silently=False,
    )
    print("✅ Confirmation email sent!")

def notify_admin(application):
    """Send a notification email to the admin about a new application."""
    print("📩 Sending admin notification email")  # Debug print
    send_mail(
        subject="New Non-Coliver Application Submitted",
        message=f"A new application has been submitted.\n\n"
                f"Name: {application.first_name} {application.last_name}\n"
                f"Email: {application.email}\n"
                f"Phone: {application.phone}\n"
                f"Resume: {application.resume.url if application.resume else 'No file uploaded'}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=["guesswhat793@gmail.com"],  # Replace with actual admin email
        fail_silently=False,
    )
    print("✅ Admin notification email sent!")
