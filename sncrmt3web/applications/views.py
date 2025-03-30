from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db import models
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .forms import ApplicationDatesForm, ApplicationNameForm, ApplicationEditForm          
from chapters.models import Chapter, ChapterBooking
from .models import Application
from colivers.models import Coliver

@login_required
def applications_list(request):
    applications = Application.objects.filter(created_by=request.user, is_hidden=False)

    return render(request, 'applications/applications_list.html', {
        'applications': applications
    })  

@login_required
def application_detail(request, pk): #shows application details
    application = Application.objects.filter(created_by=request.user, is_hidden=False).get(pk=pk)

    return render(request, 'applications/application_detail.html', {
        'application': application
    })

@login_required
def applications(request):
    print("=== Starting applications view ===")
    if request.method == 'POST':
        print("POST request received")
        form = ApplicationDatesForm(request.POST)
        print(f"Form data: {request.POST}")
        print(f"check_availability in POST: {request.POST.getlist('check_availability')}")

        if form.is_valid():
            print("Form is valid")
            date_join = form.cleaned_data['date_join']
            date_leave = form.cleaned_data['date_leave']
            guests = form.cleaned_data['guests']
            member_type = form.cleaned_data['member_type']
            print(f"Dates: {date_join} to {date_leave}")
            print(f"Guests: {guests}, Member type: {member_type}")

            # Calculate number of nights
            nights = (date_leave - date_join).days
            print(f"Number of nights: {nights}")

            # Get all chapters with availability status
            chapters_with_availability = []
            all_chapters = Chapter.objects.prefetch_related('images').all()
            print(f"Total chapters found: {all_chapters.count()}")
            
            for chapter in all_chapters:
                print(f"\nChecking chapter: {chapter.name}")
                is_available = True
                # Check for conflicting bookings
                conflicting_bookings = Application.objects.filter(
                    chapter=chapter,
                    application_status__in=['Accepted', 'Waiting list', 'Pending'],
                    date_join__lt=date_leave,
                    date_leave__gt=date_join,
                    is_hidden=False  # Only check non-hidden applications
                )
                print(f"Conflicting bookings query: {conflicting_bookings.query}")
                print(f"Number of conflicting bookings: {conflicting_bookings.count()}")
                
                if conflicting_bookings.exists():
                    is_available = False
                    print(f"Chapter {chapter.name} is NOT available")
                else:
                    print(f"Chapter {chapter.name} is available")

                chapters_with_availability.append({
                    'chapter': chapter,
                    'is_available': is_available
                })

            # If just checking availability
            if 'check_availability' in request.POST:
                print("\nChecking availability...")
                # Calculate costs for all chapters and include images
                chapters_info = []
                for chapter_data in chapters_with_availability:
                    chapter = chapter_data['chapter']
                    total_cost = chapter.cost_per_night * nights
                    chapter_info = {
                        'chapter': chapter,
                        'is_available': chapter_data['is_available'],
                        'nightly_rate': chapter.cost_per_night,
                        'total_cost': round(total_cost, 2),
                        'nights': nights,
                        'images': chapter.images.all()
                    }
                    chapters_info.append(chapter_info)
                    print(f"Chapter info added: {chapter.name} - Available: {chapter_data['is_available']}")

                print(f"\nTotal chapters info: {len(chapters_info)}")
                print("Rendering template with chapters_info")
                return render(request, 'applications/new_application.html', {
                    'form': form,
                    'chapters_info': chapters_info,
                    'dates_selected': True,
                    'form_data': {
                        'date_join': date_join.strftime('%Y-%m-%d'),
                        'date_leave': date_leave.strftime('%Y-%m-%d'),
                        'guests': guests,
                        'member_type': member_type
                    }
                })
        else:
            print("Form is invalid")
            print(f"Form errors: {form.errors}")
            print(f"Form non field errors: {form.non_field_errors()}")
            return render(request, 'applications/new_application.html', {
                'form': form,
                'chapters_info': [],
                'dates_selected': False,
                'form_data': request.POST
            })

    else:
        form = ApplicationDatesForm()

    return render(request, 'applications/new_application.html', {
        'form': form,
        'chapters_info': [],
        'dates_selected': False,
        'form_data': None
    })

@login_required
def available_chapters(request):
    application_data = request.session.get('application_data')
    if not application_data:
        return redirect('applications')  # Go back to step 1 if no data

    date_join = datetime.fromisoformat(application_data['date_join'])
    date_leave = datetime.fromisoformat(application_data['date_leave'])

    # Get all chapters
    all_chapters = Chapter.objects.all()
    available_chapters = []

    for chapter in all_chapters:
        # Check if chapter has any conflicting bookings
        conflicting_bookings = ChapterBooking.objects.filter(
            chapter=chapter
        ).filter(
            models.Q(start_date__lte=date_leave) & 
            models.Q(end_date__gte=date_join)
        ).exists()

        if not conflicting_bookings:
            available_chapters.append(chapter)

    if request.method == 'POST':
        selected_chapter = request.POST.get('chapter')
        if selected_chapter:
            # Create and save the initial application with all fields
            application = Application.objects.create(
                created_by=request.user,
                first_name=application_data['first_name'],
                last_name=application_data['last_name'],
                email=application_data['email'],
                date_join=date_join,
                date_leave=date_leave,
                guests=application_data['guests'],
                member_type=application_data['member_type']
            )
            
            # Store the application ID in session for future steps
            request.session['application_id'] = application.id
            request.session['application_data']['chapter_id'] = selected_chapter
            return redirect('application_step2')

    return render(request, 'applications/available_chapters.html', {
        'chapters': available_chapters
    })

@login_required
def application_step2(request):
    # Get the application from session
    application_id = request.session.get('application_id')
    if not application_id:
        return redirect('applications')
    
    application = get_object_or_404(Application, id=application_id, created_by=request.user)

    if request.method == 'POST':
        form = ApplicationNameForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save(commit=False)
            
            # If submitting, mark as submitted
            if 'submit' in request.POST:
                application.status = Application.STATUS_SUBMITTED
            
            application.save()

            # Clear the session data
            if 'application_id' in request.session:
                del request.session['application_id']

            messages.success(request, "Your application has been successfully saved!")
            return redirect('applications_list')
    else:
        form = ApplicationNameForm(instance=application)

    return render(request, 'applications/application_step2.html', {
        'form': form,
        'application': application
    })

@login_required
def application_success(request):
    return render(request, 'applications/application_success.html')

@login_required
def edit_application(request, pk):
    application = get_object_or_404(Application, pk=pk, created_by=request.user)
    
    if not application.is_editable:
        messages.error(request, "This application has already been submitted and cannot be edited.")
        return redirect('application_detail', pk=application.pk)
    
    if request.method == 'POST':
        form = ApplicationEditForm(request.POST, instance=application)
        if form.is_valid():
            date_join = form.cleaned_data['date_join']
            date_leave = form.cleaned_data['date_leave']
            
            # Check minimum stay duration
            min_leave_date = date_join + timedelta(days=28)
            if date_leave < min_leave_date:
                messages.error(request, mark_safe('<strong style="color: red;">Bookings must be for at least a month!</strong>'))
                return render(request, 'applications/edit_application.html', {
                    'form': form,
                    'application': application,
                    'available_chapters': [],
                    'current_chapter': application.chapter,
                    'dates_changed': True
                })

            # Get all chapters with availability status
            chapters_with_availability = get_available_chapters(date_join, date_leave)
            nights = (date_leave - date_join).days
            
            # Calculate costs for all chapters and include images
            chapters_info = []
            for chapter_data in chapters_with_availability:
                chapter = chapter_data['chapter']
                total_cost = chapter.cost_per_night * nights
                chapters_info.append({
                    'chapter': chapter,
                    'is_available': chapter_data['is_available'],
                    'nightly_rate': chapter.cost_per_night,
                    'total_cost': round(total_cost, 2),
                    'nights': nights,
                    'images': chapter.images.all()
                })

            # If just checking availability
            if 'check_availability' in request.POST:
                current_chapter_costs = None
                if application.chapter:
                    current_chapter_costs = {
                        'nightly_rate': application.chapter.cost_per_night,
                        'total_cost': round(application.chapter.cost_per_night * nights, 2),
                        'nights': nights,
                        'images': application.chapter.images.all()
                    }
                
                return render(request, 'applications/edit_application.html', {
                    'form': form,
                    'application': application,
                    'available_chapters': chapters_info,
                    'current_chapter': application.chapter,
                    'current_chapter_costs': current_chapter_costs,
                    'dates_changed': True
                })
            
            # Handle save or submit
            application = form.save(commit=False)
            
            # If submitting, update the status
            if 'submit' in request.POST:
                application.status = Application.STATUS_SUBMITTED
                application.application_status = Application.STATUS_SUBMITTED
                messages.success(request, "Your application has been successfully submitted!")
            else:
                messages.success(request, "Your changes have been saved!")
            
            application.save()
            return redirect('applications_list')

    else:
        form = ApplicationEditForm(instance=application)
        # Get available chapters and calculate costs for initial load
        if application.date_join and application.date_leave:
            chapters_with_availability = get_available_chapters(application.date_join, application.date_leave)
            nights = (application.date_leave - application.date_join).days
            
            chapters_info = []
            for chapter_data in chapters_with_availability:
                chapter = chapter_data['chapter']
                total_cost = chapter.cost_per_night * nights
                chapters_info.append({
                    'chapter': chapter,
                    'is_available': chapter_data['is_available'],
                    'nightly_rate': chapter.cost_per_night,
                    'total_cost': round(total_cost, 2),
                    'nights': nights,
                    'images': chapter.images.all()
                })

            # Calculate current chapter costs if it exists
            current_chapter_costs = None
            if application.chapter:
                current_chapter_costs = {
                    'nightly_rate': application.chapter.cost_per_night,
                    'total_cost': round(application.chapter.cost_per_night * nights, 2),
                    'nights': nights,
                    'images': application.chapter.images.all()
                }
        else:
            chapters_info = []
            current_chapter_costs = None
            nights = None

    # Get current chapter info
    current_chapter = None
    current_chapter_costs = None
    if application.chapter:
        current_chapter = application.chapter  # This will include related images through chapter.images.all()
        current_chapter_costs = {
            'nightly_rate': current_chapter.cost_per_night,
            'nights': nights,
            'total_cost': current_chapter.cost_per_night * nights
        }

    # Get available chapters
    available_chapters = []
    if application.date_join and application.date_leave:
        # Get all chapters with their images
        all_chapters = Chapter.objects.prefetch_related('images').all()
        
        for chapter in all_chapters:
            is_available = True
            # Check for conflicting bookings
            conflicting_bookings = Application.objects.filter(
                chapter=chapter,
                status__in=['approved', 'pending'],
                date_join__lt=application.date_leave,
                date_leave__gt=application.date_join
            ).exclude(id=application.id)
            
            if conflicting_bookings.exists():
                is_available = False

            chapter_info = {
                'chapter': chapter,  # This chapter object includes related images
                'is_available': is_available,
                'nightly_rate': chapter.cost_per_night,
                'nights': nights,
                'total_cost': chapter.cost_per_night * nights
            }
            available_chapters.append(chapter_info)

    return render(request, 'applications/edit_application.html', {
        'application': application,
        'form': form,
        'current_chapter': current_chapter,
        'current_chapter_costs': current_chapter_costs,
        'available_chapters': available_chapters,
        'dates_changed': False,
    })

def get_available_chapters(date_join, date_leave):
    """Helper function to get all chapters and check their availability for given dates"""
    if not date_join or not date_leave:
        return []
        
    all_chapters = Chapter.objects.all()
    chapters_with_availability = []

    for chapter in all_chapters:
        # Check for conflicting bookings
        conflicting_bookings = ChapterBooking.objects.filter(
            chapter=chapter,
            start_date__lt=date_leave,
            end_date__gt=date_join
        ).exists()

        # Add chapter to list with availability status
        chapters_with_availability.append({
            'chapter': chapter,
            'is_available': not conflicting_bookings
        })
    
    return chapters_with_availability

@require_http_methods(["POST"])
def check_availability(request):
    try:
        data = json.loads(request.body)
        date_join = datetime.strptime(data.get('date_join'), '%Y-%m-%d').date()
        date_leave = datetime.strptime(data.get('date_leave'), '%Y-%m-%d').date()
        guests = int(data.get('guests', 1))
        member_type = data.get('member_type', 'new member')

        # Validate required fields
        if not all([date_join, date_leave, guests, member_type]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Validate dates
        if date_join >= date_leave:
            return JsonResponse({'error': 'Check-in date must be before check-out date'}, status=400)

        # Validate guest count
        if guests < 1 or guests > 3:
            return JsonResponse({'error': 'Number of guests must be between 1 and 3'}, status=400)

        # Get all chapters with availability status
        chapters_with_availability = []
        all_chapters = Chapter.objects.prefetch_related('images').all()
        
        for chapter in all_chapters:
            is_available = True
            # Check for conflicting bookings in Colivers table
            conflicting_colivers = Coliver.objects.filter(
                chapter=chapter,
                arrival_date__lt=date_leave,
                departure_date__gt=date_join
            )
            
            if conflicting_colivers.exists():
                is_available = False

            chapters_with_availability.append({
                'chapter': {
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                    'cost_per_night': chapter.cost_per_night
                },
                'is_available': is_available,
                'nightly_rate': chapter.cost_per_night,
                'images': [{'url': image.image.url} for image in chapter.images.all()]
            })

        return JsonResponse({'chapters': chapters_with_availability})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

@require_http_methods(["POST"])
@login_required
def create_application(request):
    try:
        data = json.loads(request.body)
        print("\n=== Starting create_application ===")
        print(f"Received data: {data}")
        
        # Validate required fields
        required_fields = ['chapter_id', 'first_name', 'last_name', 'email', 
                         'date_join', 'date_leave', 'guests', 'member_type',
                         'question_1', 'question_2', 'question_3']
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                return JsonResponse({
                    'error': f'Missing required field: {field}'
                }, status=400)

        # Validate dates
        try:
            date_join = datetime.strptime(data['date_join'], '%Y-%m-%d').date()
            date_leave = datetime.strptime(data['date_leave'], '%Y-%m-%d').date()
            print(f"\nParsed dates: {date_join} to {date_leave}")
        except ValueError:
            return JsonResponse({
                'error': 'Invalid date format. Please use YYYY-MM-DD format.'
            }, status=400)

        # Validate date range
        if date_leave <= date_join:
            return JsonResponse({
                'error': 'Check-out date must be after check-in date'
            }, status=400)

        min_leave_date = date_join + timedelta(days=28)
        max_leave_date = date_join + timedelta(days=62)
        
        if date_leave < min_leave_date:
            return JsonResponse({
                'error': 'Bookings must be for at least 1 month'
            }, status=400)
        if date_leave > max_leave_date:
            return JsonResponse({
                'error': 'Initial bookings cannot exceed 2 months'
            }, status=400)

        # Validate guests
        try:
            guests = int(data['guests'])
            if guests < 1 or guests > 3:
                return JsonResponse({
                    'error': 'Number of guests must be between 1 and 3'
                }, status=400)
            # Convert guests to string format as per model choices
            guests = str(guests)  # This ensures we store it as a string
            if guests not in [Application.COUPLE, Application.INDIVIDUAL]:
                return JsonResponse({
                    'error': 'Invalid number of guests'
                }, status=400)
            print(f"\nValidated guests: {guests}")
        except ValueError:
            return JsonResponse({
                'error': 'Invalid number of guests'
            }, status=400)

        # Validate member type
        if data['member_type'] not in [Application.NEW, Application.RETURNING]:
            return JsonResponse({
                'error': 'Invalid member type'
            }, status=400)
        print(f"\nValidated member type: {data['member_type']}")

        # Validate questions
        if not data['question_1'].strip() or not data['question_2'].strip() or not data['question_3'].strip():
            return JsonResponse({
                'error': 'All questions must be answered'
            }, status=400)

        # Check if chapter exists and is available
        try:
            chapter = Chapter.objects.get(id=data['chapter_id'])
            print(f"\nFound chapter: {chapter.name}")
            
            # Check if chapter has any Accepted applications
            conflicting_bookings = Application.objects.filter(
                chapter=chapter,
                application_status=Application.STATUS_ACCEPTED,  # Use the model's constant
                date_join__lt=date_leave,
                date_leave__gt=date_join,
                is_hidden=False  # Only check non-hidden applications
            )
            print(f"Conflicting bookings query: {conflicting_bookings.query}")
            print(f"Number of conflicting bookings: {conflicting_bookings.count()}")
            
            if conflicting_bookings.exists():
                print("\nFound conflicting bookings:")
                for booking in conflicting_bookings:
                    print(f"- ID: {booking.id}")
                    print(f"- Status: {booking.application_status}")
                    print(f"- Dates: {booking.date_join} to {booking.date_leave}")
                    print(f"- Created by: {booking.created_by}")
                    print(f"- Is hidden: {booking.is_hidden}")
                return JsonResponse({
                    'error': 'Selected room is no longer available for these dates'
                }, status=400)
            else:
                print("\nNo conflicting bookings found")
        except Chapter.DoesNotExist:
            return JsonResponse({
                'error': 'Selected room not found'
            }, status=400)

        # Create application
        print("\nCreating application...")
        application = Application.objects.create(
            created_by=request.user,  # Set created_by to the user who submitted the application
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            date_join=date_join,
            date_leave=date_leave,
            guests=guests,
            chapter=chapter,
            status='pending',
            application_status='Pending',
            member_type=data['member_type'],
            question_1=data['question_1'],
            question_2=data['question_2'],
            question_3=data['question_3']
        )
        print(f"Application created successfully with ID: {application.id}")

        # Calculate total cost
        total_cost = application.calculate_cost()
        print(f"Total cost calculated: {total_cost}")

        return JsonResponse({
            'success': True,
            'application_id': application.id,
            'redirect_url': '/dashboard/applications/',
            'total_cost': float(total_cost)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"\nError creating application: {str(e)}")
        return JsonResponse({
            'error': f'Server error: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
@login_required
def apply_coupon(request):
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')
        total_price = float(data.get('total_price', 0))

        # Here you would typically validate the coupon code against your database
        # For now, we'll implement a simple discount logic
        if coupon_code.upper() == 'WELCOME10':
            discount = 0.10  # 10% discount
            discounted_price = total_price * (1 - discount)
            return JsonResponse({
                'success': True,
                'discounted_price': round(discounted_price, 2),
                'discount_percentage': 10
            })
        elif coupon_code.upper() == 'SUMMER20':
            discount = 0.20  # 20% discount
            discounted_price = total_price * (1 - discount)
            return JsonResponse({
                'success': True,
                'discounted_price': round(discounted_price, 2),
                'discount_percentage': 20
            })
        else:
            return JsonResponse({'error': 'Invalid coupon code'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import ApplicationForm
from .models import Application
@login_required
def applications_list(request):
    applications = Application.objects.filter(created_by = request.user)

    return render(request, 'applications/applications_list.html', {
        'applications': applications
    })  

@login_required
def application_detail(request, pk): #shows application details
    application = Application.objects.filter(created_by = request.user).get(pk=pk)

    return render(request, 'applications/application_detail.html', {
        'application': application
    })

@login_required
def applications(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)

        if form.is_valid():
            application = form.save(commit=False)
            application.created_by = request.user
            application.save()

            return redirect('dashboard')
    else:
        form = ApplicationForm()

    return render(request, 'applications/new_application.html', {
        'form': form
    })

'''