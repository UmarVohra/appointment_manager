from anaconda_cloud_auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AppointmentForm, AdminAppointmentForm, AdminCreationForm, AdminProfileForm
from .models import Appointment, AdminProfile
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.db import IntegrityError
from django.core.paginator import Paginator
from datetime import datetime, date, timedelta
import pandas as pd
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.db.models import Case, When, IntegerField
from django.template.loader import render_to_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os
load_dotenv()
# Create your views here.
# Placeholder for appointments app views

def is_admin(user):
    return user.is_authenticated and user.is_staff

def landing_page(request):
    doctor = User.objects.filter(profile__is_doctor=True).first()
    return render(request, 'landing.html', {'doctor': doctor})


def book_appointment(request):
    booked = list(Appointment.objects.values_list('date', 'slot'))

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        
        if form.is_valid():
            try:
                booking = form.save()  # save booking

                # prepare email data
                subject = "Appointment Confirmation ✅"
                from_email = os.getenv("DEFAULT_FROM_EMAIL")
                to_email = booking.email  # send to the user

                # HTML content
                html_content = render_to_string("emails/appointment_confirmation.html", {
                    "name": booking.fullname,
                    "date": booking.date,
                    "slot": booking.slot,
                    "department": booking.department,
                })

                # Gmail SMTP via Django
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=html_content,
                    from_email=from_email,
                    to=[to_email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                messages.success(request, 'Appointment booked successfully! Confirmation email sent.')
                return redirect('landing_page')

            except Exception as e:
                if 'unique_constraint' in str(e).lower():
                    messages.error(request, 'This slot is already booked. Please choose another slot.')
                else:
                    messages.error(request, f'An error occurred while booking the appointment. Please try again. {str(e)}')
    else:
        form = AppointmentForm()
    
    return render(request, 'book_appointment.html', {'form': form, 'booked': booked})

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")  
        
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, "Invalid Email or Password")
            return render(request, "admin/login.html")

        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)  
            else:   
                request.session.set_expiry(60 * 60 * 24 * 30)

            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid Email or Password")

    return render(request, "admin/login.html")

def handle_edit_appointment_form(request, appointment_id=None):
    """Handle appointment form submission for updating or deleting."""
    form = AdminAppointmentForm()  # Default form for return
    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if request.POST.get('delete'):
            appointment.delete()
            messages.success(request, 'Appointment deleted successfully.')
            return redirect(request.META.get('HTTP_REFERER', '/')), form

        form = AdminAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Appointment updated successfully.')
                return redirect(request.META.get('HTTP_REFERER', '/')), AdminAppointmentForm()  # Return fresh form after success
            except IntegrityError:
                form_date = form.cleaned_data.get('date') if hasattr(form, 'cleaned_data') else None
                slot = form.cleaned_data.get('slot') if hasattr(form, 'cleaned_data') else None
                if form_date and slot:
                    Appointment.objects.filter(date=form_date, slot=slot).exclude(pk=appointment.pk).delete()
                    try:
                        form.save()
                        messages.success(request, 'Appointment updated successfully.')
                        return redirect(request.META.get('HTTP_REFERER', '/')), AdminAppointmentForm()  # Return fresh form
                    except Exception:
                        messages.error(request, 'Could not update appointment after removing conflicts.')
                else:
                    messages.error(request, 'Could not update appointment due to uniqueness constraint.')
            messages.error(request, 'Could not update appointment. See form errors.')
            return None, form  # Return form with errors
    return None, form  # Default case: no redirect, return default form


def handle_add_appointment_form(request):
    """Handle form submission for adding a new appointment."""
    form = AdminAppointmentForm()  # Default form
    if request.method == "POST" and request.POST.get('action') == 'add':
        form = AdminAppointmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Appointment added successfully.')
                return redirect('admin_dashboard'), AdminAppointmentForm()  # Return fresh form
            except IntegrityError:
                messages.error(request, 'Could not add appointment due to slot conflict.')
            except Exception:
                messages.error(request, 'An error occurred while adding the appointment.')
            messages.error(request, 'Please fix the errors below.')
            return None, form  # Return form with errors
    return None, form  # Default case: no redirect, return default form


def filter_appointments(request):
    """Apply filters and search queries to today's appointments only."""
    today = date.today()
    appointments = Appointment.objects.filter(date=today).annotate(
        is_pending=Case(
            When(status='pending', then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('is_pending', 'date', 'slot')

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status')

    if status:
        appointments = appointments.filter(status=status)

    if query:
        q_obj = Q()
        # Date search (restrict to today)
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                parsed_date = datetime.strptime(query, fmt).date()
                if parsed_date == today:  # Only include if date matches today
                    q_obj |= Q(date=parsed_date)
                break
            except ValueError:
                continue
        # Numeric search
        if query.isdigit():
            q_obj |= Q(age=query) | Q(phone__icontains=query) | Q(enroll_no__icontains=query)
        # String search
        q_obj |= (
            Q(fullname__icontains=query) |
            Q(department__icontains=query) |
            Q(reason__icontains=query) |
            Q(email__icontains=query) |
            Q(slot__icontains=query)
        )
        appointments = appointments.filter(q_obj)

    return Paginator(appointments, 10).get_page(request.GET.get('page'))


def get_dashboard_stats():
    """Calculate dashboard statistics for appointments."""
    all_appointments = Appointment.objects.all()
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    today_count = all_appointments.filter(date=today).count()
    week_count = all_appointments.filter(date__range=(start_of_week, end_of_week)).count()
    pending_count = all_appointments.filter(status__iexact='pending').count()
    completed_count = all_appointments.filter(status__iexact='completed').count()

    return {
        'today_count': today_count,
        'week_count': week_count,
        'pending_count': pending_count,
        'completed_count': completed_count,
    }


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Render admin dashboard with appointment list, stats, and separate add/edit forms."""
    # Handle form submissions
    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        if appointment_id:
            # Handle edit or delete
            redirect_response, edit_form = handle_edit_appointment_form(request, appointment_id)
            add_form = AdminAppointmentForm()  # Fresh form for add
            if redirect_response:
                return redirect_response
        elif request.POST.get('action') == 'add':
            # Handle add
            redirect_response, add_form = handle_add_appointment_form(request)
            edit_form = AdminAppointmentForm()  # Fresh form for edit
            if redirect_response:
                return redirect_response
        else:
            edit_form = AdminAppointmentForm()
            add_form = AdminAppointmentForm()
    else:
        edit_form = AdminAppointmentForm()
        add_form = AdminAppointmentForm()

    # Get filtered appointments and stats
    page_obj = filter_appointments(request)
    stats = get_dashboard_stats()

    return render(request, "admin/dashboard.html", {
        "page_obj": page_obj,
        "form": edit_form,  # For editing appointments
        "addForm": add_form,  # For adding new appointments
        **stats,
    })


@login_required
@user_passes_test(is_admin)
def admin_add_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment added successfully.")
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = AppointmentForm()

    return render(request, "admin/add-appointment.html", {"form": form})


def admin_appointments(request):
    appointments = Appointment.objects.all()
    edit_form = AdminAppointmentForm()
    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        if appointment_id:
            # Handle edit or delete
            redirect_response, edit_form = handle_edit_appointment_form(request, appointment_id)
            if redirect_response:
                return redirect_response
    # Apply date range filters
    start_date_str = request.GET.get('startDate')
    end_date_str = request.GET.get('endDate')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            appointments = appointments.filter(date__gte=start_date)
        except ValueError:
            pass  # Ignore invalid date

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            appointments = appointments.filter(date__lte=end_date)
        except ValueError:
            pass  # Ignore invalid date

    # Apply search query
    query = request.GET.get('q', '').strip()
    if query:
        q_obj = Q()
        # Date search
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                parsed_date = datetime.strptime(query, fmt).date()
                q_obj |= Q(date=parsed_date)
                break
            except ValueError:
                continue
        # Numeric search
        if query.isdigit():
            q_obj |= Q(age=int(query)) | Q(phone__icontains=query) | Q(enroll_no__icontains=query)
        # String search
        q_obj |= (
            Q(fullname__icontains=query) |
            Q(department__icontains=query) |
            Q(reason__icontains=query) |
            Q(email__icontains=query) |
            Q(slot__icontains=query) |
            Q(status__icontains=query)
        )
        appointments = appointments.filter(q_obj)

    # Ordering
    appointments = appointments.order_by('-date', 'slot')

    # Pagination
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/find_appointment.html", {"page_obj": page_obj, "form": edit_form})

@login_required
@user_passes_test(is_admin)
def add_admin(request):
    if request.method == 'POST':
        form = AdminCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New admin created successfully.')
            return redirect('manage_admins')
        else:
            messages.error(request, 'Please fix the errors below.')
            # render the manage page with the invalid add_form and a fresh edit_form
            admins = User.objects.filter().select_related('profile')
            edit_form = AdminCreationForm()
            # make edit_form's image and password fields optional for editing
            if 'image' in edit_form.fields:
                edit_form.fields['image'].required = False
                edit_form.fields['image'].widget.attrs.update({'id': 'edit-image-input', 'class': 'form-input image-upload-input'})
            if 'password1' in edit_form.fields:
                edit_form.fields['password1'].required = False
            if 'password2' in edit_form.fields:
                edit_form.fields['password2'].required = False

            return render(request, 'admin/manage-admin.html', {'add_form': form, 'edit_form': edit_form, 'admins': admins})
    else:
        return redirect('manage_admins')


@login_required
@user_passes_test(is_admin)
def edit_admin(request, user_id):
    # Edit an existing admin (POST only via modal)
    user = get_object_or_404(User, pk=user_id, is_staff=True)
    profile = getattr(user, 'profile', None)

    if request.method != 'POST':
        messages.error(request, 'Invalid request method for editing admin.')
        return redirect('manage_admins')

    # Prepare data for updating user and profile
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    qualification = request.POST.get('qualification', '').strip()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')

    # Basic validations
    if not first_name or not last_name or not email:
        messages.error(request, 'First name, last name and email are required.')
        return redirect('manage_admins')

    # Update user fields
    user.first_name = first_name
    user.last_name = last_name
    user.email = email

    # Handle optional password change
    if password1 or password2:
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('manage_admins')
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('manage_admins')
        user.set_password(password1)

    # Profile update
    if profile:
        profile.phone = phone
        profile.qualification = qualification
        # handle image upload if present
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
    else:
        # create profile if missing
        profile = AdminProfile(user=user, phone=phone, qualification=qualification)
        if 'image' in request.FILES:
            profile.image = request.FILES['image']

    try:
        user.save()
        profile.user = user
        profile.save()
        messages.success(request, 'Admin updated successfully.')
    except Exception as e:
        messages.error(request, f'Error updating admin: {str(e)}')

    # Redirect based on caller; allow templates to request return to 'profile'
    next_dest = request.POST.get('next', '').strip().lower()
    if next_dest == 'profile':
        return redirect('admin_profile')
    return redirect('manage_admins')


@login_required
@user_passes_test(is_admin)
def delete_admin(request, user_id):
    # Only allow POST deletes
    if request.method != 'POST':
        messages.error(request, 'Invalid request method for deleting admin.')
        return redirect('manage_admins')

    # Prevent deleting self
    if request.user.pk == int(user_id):
        messages.error(request, 'You cannot delete your own account.')
        return redirect('manage_admins')

    try:
        user = User.objects.get(pk=user_id, is_staff=True)
    except User.DoesNotExist:
        messages.error(request, 'Admin not found.')
        return redirect('manage_admins')

    try:
        # Delete related AdminProfile if exists
        try:
            profile = getattr(user, 'profile', None)
            if profile:
                profile.delete()
        except Exception:
            pass

        user.delete()
        messages.success(request, 'Admin deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting admin: {str(e)}')

    return redirect('manage_admins')

@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    edit_form = AdminCreationForm()
    if 'image' in edit_form.fields:
        edit_form.fields['image'].required = False
        edit_form.fields['image'].widget.attrs.update({'id': 'edit-image-input', 'class': 'form-input image-upload-input'})
    if 'password1' in edit_form.fields:
        edit_form.fields['password1'].required = False
    if 'password2' in edit_form.fields:
        edit_form.fields['password2'].required = False
    return render(request, 'admin/profile.html', {'edit_form': edit_form})
@login_required
@user_passes_test(is_admin)
def admin_logout(request):
     logout(request)
     return redirect('login')


@login_required
@user_passes_test(is_admin)
def manage_admins(request):
    add_form = AdminCreationForm()
    edit_form = AdminCreationForm()
    # make image optional for edit form and give the file input a stable id for JS
    if 'image' in edit_form.fields:
        edit_form.fields['image'].required = False
        edit_form.fields['image'].widget.attrs.update({'id': 'edit-image-input', 'class': 'form-input image-upload-input'})
    # make password fields optional for edit usage
    if 'password1' in edit_form.fields:
        edit_form.fields['password1'].required = False
    if 'password2' in edit_form.fields:
        edit_form.fields['password2'].required = False

    admins = User.objects.filter().select_related("profile")
    return render(request, 'admin/manage-admin.html', {'add_form': add_form, 'edit_form': edit_form, 'admins': admins})




@login_required
@user_passes_test(is_admin)
def download_appointments_excel(request):
    # Start with all appointments
    appointments = Appointment.objects.all()

    # Apply date range filters
    start_date_str = request.GET.get('startDate')
    end_date_str = request.GET.get('endDate')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            appointments = appointments.filter(date__gte=start_date)
        except ValueError:
            pass  # Ignore invalid date

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            appointments = appointments.filter(date__lte=end_date)
        except ValueError:
            pass  # Ignore invalid date

    # Apply search query
    query = request.GET.get('q', '').strip()
    if query:
        q_obj = Q()
        # Date search
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                parsed_date = datetime.strptime(query, fmt).date()
                q_obj |= Q(date=parsed_date)
                break
            except ValueError:
                continue
        # Numeric search
        if query.isdigit():
            q_obj |= Q(age=int(query)) | Q(phone__icontains=query) | Q(enroll_no__icontains=query)
        # String search
        q_obj |= (
            Q(fullname__icontains=query) |
            Q(department__icontains=query) |
            Q(reason__icontains=query) |
            Q(email__icontains=query) |
            Q(slot__icontains=query) |
            Q(status__icontains=query)
        )
        appointments = appointments.filter(q_obj)

    # Fetch filtered data
    qs = appointments.values(
        "id", "fullname", "age", "enroll_no", "department",
        "phone", "email", "reason", "date", "slot",
        "status", "remarks", "created_at", "updated_at"
    )

    # Convert to DataFrame
    df = pd.DataFrame(list(qs))

    # If no data, create empty dataframe with headers
    if df.empty:
        df = pd.DataFrame(columns=[
            "id", "fullname", "age", "enroll_no", "department",
            "phone", "email", "reason", "date", "slot",
            "status", "remarks", "created_at", "updated_at"
        ])

    # Convert datetime fields to string for Excel readability
    if "created_at" in df:
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
    if "updated_at" in df:
        df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%Y-%m-%d %H:%M")
    if "date" in df:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    # Create HTTP response with Excel file
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="appointments.xlsx"'

    # Write dataframe to Excel
    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Appointments", index=False)

    return response

@login_required
@user_passes_test(is_admin)
def set_doctor(request, id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=id, is_staff=True)
        profile = getattr(user, 'profile', None)
        profile.is_doctor = True
        profile.save()
        messages.success(request, f'{user.get_full_name()} is now set as a doctor.')
        return redirect('manage_admins')
    
def remove_doctor(request, id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=id, is_staff=True)
        profile = getattr(user, 'profile', None)
        profile.is_doctor = False
        profile.save()
        messages.success(request, f'{user.get_full_name()} is no longer a doctor.')
        return redirect('manage_admins')