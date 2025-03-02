from django.shortcuts import render, redirect
from django.contrib import messages
from crm.forms.noncoliver_forms import NoncoliverForm
from mailing.utils.mailing_utils import send_application_confirmation, notify_admin  # Import mailing functions

def apply_noncoliver(request):
    print("DEBUG: apply_noncoliver view called")  # <-- Debug print

    if request.method == "POST":
        print("DEBUG: Received POST request")  # <-- Debug print

        form = NoncoliverForm(request.POST, request.FILES)
        if form.is_valid():
            print("DEBUG: Form is valid")  # <-- Debug print
            
            application = form.save()

            # Call the separate mailing functions
            send_application_confirmation(application)
            notify_admin(application)

            messages.success(request, "Application submitted successfully!")
            return redirect("apply")  # Make sure "apply" is the correct URL name
        else:
            print("DEBUG: Form is invalid", form.errors)  # <-- Debug print

    else:
        print("DEBUG: Received GET request")  # <-- Debug print
        form = NoncoliverForm()

    return render(request, "crm/apply.html", {"form": form})
