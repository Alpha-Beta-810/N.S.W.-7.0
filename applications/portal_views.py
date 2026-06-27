"""
portal_views.py  —  All admin portal views. Lives alongside views.py.
URL prefix:  /portal/
"""
import io
import calendar

from datetime import timedelta
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseForbidden

from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .models import Application, Project

User = get_user_model()

# ═══════════════════════════════════════════════════════════════
# RBAC GUARD
# ═══════════════════════════════════════════════════════════════

def is_last_two_days_of_month():
    """Returns True if today is the last or second-to-last day of the month."""
    today = date.today()
    # calendar.monthrange returns (first_weekday, number_of_days_in_month)
    last_day = calendar.monthrange(today.year, today.month)[1]
    
    # If today's date is greater than or equal to (last_day - 1)
    return today.day >= (last_day - 1)

'''def is_portal_staff(user):
    """Returns True for SuperAdmins and Reviewers. Raises 403 otherwise."""
    print(f"\n🚪 --- GATEKEEPER CHECK FOR: '{user.username}' ---")
    
    if user.is_authenticated:
        if user.is_superuser:
            print("✅ Access Granted: Superuser")
            return True
            
        if user.groups.filter(name='Reviewer').exists():
            print("👤 User is confirmed as a Reviewer.")
            
            # .strip() catches accidental spaces like "Scientist "
            if user.username.strip().lower() == 'scientist':
                from django.utils import timezone
                import calendar
                
                today = timezone.localtime().date()
                last_day = calendar.monthrange(today.year, today.month)[1]
                
                is_end_of_month = today.day >= (last_day - 1)
                is_test_day = (today.month == 5 and today.day == 25)
                
                print(f"📅 Server Date: {today}")
                print(f"🌙 Is End of month?: {is_end_of_month}")
                print(f"🧪 Is Test Day (May 25)?: {is_test_day}")
                
                if not (is_end_of_month or is_test_day):
                    print("❌ Access Denied: Date conditions not met.")
                    raise PermissionDenied 
                
                print("✅ Access Granted: Backdoor condition met!")
                return True
            
            # For all other Reviewers
            print("✅ Access Granted: Standard Reviewer")
            return True
            
    print("❌ Access Denied: Fallback rejection.")
    raise PermissionDenied'''
    
def is_portal_staff(user):
    """Returns True for SuperAdmins and Reviewers. Raises 403 otherwise."""
    if user.is_authenticated:
        # Superadmins always get a free pass
        if user.is_superuser:
            return True
            
        # Check if the user is in the Reviewer group
        if user.groups.filter(name='Reviewer').exists():
            
            # --- STRICT TIME-BASED BOUNCER LOGIC ---
            if user.username.strip().lower() == 'scientist':
                from django.utils import timezone
                import calendar
                
                today = timezone.localtime().date()
                last_day = calendar.monthrange(today.year, today.month)[1]
                
                # Check if today is the last or second-to-last day of the month
                is_end_of_month = today.day >= (last_day - 1)
                
                # If it is NOT the end of the month, instantly trigger the 403 Access Denied page
                if not is_end_of_month:
                    raise PermissionDenied 
            # ---------------------------------------
            
            # If they pass the time check (or are a different Reviewer), grant access
            return True
            
    # Fallback for anyone else
    raise PermissionDenied


def portal_login_required(view_func):
    """Decorator: redirects to /login/ if not authenticated."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')
        try:
            is_portal_staff(request.user)
        except PermissionDenied:
            return render(request, 'portal/403.html', status=403)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def superadmin_required(view_func):
    """Decorator: only Django superusers allowed."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')
        if not request.user.is_superuser:
            return render(request, 'portal/403.html', status=403)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════

def portal_login(request):
    if request.user.is_authenticated:
        try:
            is_portal_staff(request.user)
            return redirect('/dashboard/')
        except PermissionDenied:
            pass

    next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard/'
    error = None

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', ''),
        )
        if user is not None:
            try:
                is_portal_staff(user)
                login(request, user)
                return redirect(next_url)
            except PermissionDenied:
                error = 'Your account does not have portal access.'
        else:
            error = 'Invalid username or password.'

    return render(request, 'portal/login.html', {'error': error, 'next': next_url})


def portal_logout(request):
    logout(request)
    return redirect('/login/')


# ═══════════════════════════════════════════════════════════════
# DASHBOARD  —  Tabbed by status
# ═══════════════════════════════════════════════════════════════

@portal_login_required
def dashboard(request):
    # --- Catch Add/Edit/Delete/Assign Actions ---
    allowed_actions = ['add_project', 'edit_project', 'delete_project', 'edit_application', 'assign_guide', 'update_status', 'update_attendance_mode']
    
    if request.method == 'POST' and request.POST.get('action') in allowed_actions:
        action = request.POST.get('action')
        
        # --- 1. Project Actions ---
        if action == 'add_project':
            Project.objects.create(
                area=request.POST.get('area'),
                title=request.POST.get('title'),
                email=request.POST.get('email')
            )
        elif action == 'edit_project':
            proj = Project.objects.get(id=request.POST.get('project_id'))
            proj.area = request.POST.get('area')
            proj.title = request.POST.get('title')
            proj.email = request.POST.get('email')
            proj.save()
            return redirect('/dashboard/?tab=projects')
            
        elif action == 'delete_project':
            Project.objects.filter(id=request.POST.get('project_id')).delete()
            return redirect('/dashboard/?tab=projects')
            
        # --- 2. Application Actions ---
        elif action == 'edit_application':
            app = Application.objects.get(id=request.POST.get('app_id'))
            app.full_name      = request.POST.get('full_name')
            app.email          = request.POST.get('email')
            app.institute_name = request.POST.get('institute_name')
            app.cgpa           = request.POST.get('cgpa')
            app.scheme         = request.POST.get('scheme')
            app.save()
            # Redirect back to whichever tab they were on
            return redirect(f"/dashboard/?tab={request.POST.get('current_tab', 'pending')}")

        elif action == 'assign_guide':
            app = Application.objects.get(id=request.POST.get('app_id'))
            
            # Destination (Database) = Source (HTML Form
            app.csir_guide_name = request.POST.get('guide')
            app.save()
            
            # Redirect back to the current tab
            current_tab = request.GET.get('tab', 'pending')
            return redirect(f'/dashboard/?tab={current_tab}')
            
        elif action == 'update_status':
            app = Application.objects.get(id=request.POST.get('app_id'))
            app.status = request.POST.get('status')
            
            # Optional: Log who changed it and when (since you already have these fields!)
            app.reviewed_by = request.user
            
            app.reviewed_at = timezone.now()
            
            app.save()
            current_tab = request.GET.get('tab', 'pending')
            return redirect(f'/dashboard/?tab={current_tab}')  
            
        elif action == 'update_attendance_mode':
                    app = Application.objects.get(id=request.POST.get('app_id'))
                    # Assuming the field in your model is named attendance_mode (or similar standard text field)
                    app.attendance_mode = request.POST.get('attendance_mode')
                    app.save()
                    current_tab = request.GET.get('tab', 'pending')
                    return redirect(f'/dashboard/?tab={current_tab}')
    # --------------------------------------------------

    active_tab = request.GET.get('tab', 'pending')
    q          = request.GET.get('q', '').strip()
    scheme     = request.GET.get('scheme', '').strip()
    area       = request.GET.get('area', '').strip()
    month      = request.GET.get('month', '').strip() # 👈 NEW: Catch the month

    # Base queryset per tab
    tab_map = {
        'pending':  Application.objects.filter(status='Pending'),
        'accepted': Application.objects.filter(status='Accepted'),
        'rejected': Application.objects.filter(status='Rejected'),
        'all':      Application.objects.all(),
    }
    qs = tab_map.get(active_tab, tab_map['pending']).order_by('-created_at')

    # Search
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(mobile__icontains=q) |
            Q(institute_name__icontains=q) |
            Q(area_of_interest__icontains=q)
        )
    if scheme:
        qs = qs.filter(scheme=scheme)
    if area:
        qs = qs.filter(area_of_interest=area)
    if month: # 👈 NEW: Filter by the application creation month
        qs = qs.filter(created_at__month=month)

    # Pagination
    paginator  = Paginator(qs, 25)
    page_obj   = paginator.get_page(request.GET.get('page'))

    # Stats for tab badges
    all_apps   = Application.objects.all()
    stats = {
        'total':    all_apps.count(),
        'pending':  all_apps.filter(status='Pending').count(),
        'accepted': all_apps.filter(status='Accepted').count(),
        'rejected': all_apps.filter(status='Rejected').count(),
    }
    week_ago = timezone.now() - timedelta(days=7)
    stats['recent'] = all_apps.filter(created_at__gte=week_ago).count()

    # Unique areas for filter dropdown
    areas = (
        Application.objects.values_list('area_of_interest', flat=True)
        .distinct()
        .exclude(area_of_interest='')
        .order_by('area_of_interest')
    )

    # ADDED 'projects' to the tab items
    TAB_ITEMS = [
        ('pending', 'Pending'), ('accepted', 'Accepted'),
        ('rejected', 'Rejected'), ('all', 'All Applications'),
        ('projects', 'Projects'),
    ]
    
    # Grab all projects to send to the template
    projects = Project.objects.all().order_by('area')
    
    # 1. Define your list of official guides (You can edit these names later)
    available_guides = [
            "Aakash Singh",
            "Ajinkya Ashok Jagtap",
            "Ateendra Gaur",
            "Basavala Bhanu Prasanth",
            "Brindashree B V",
            "Dr. Aditya Panda",
            "Dr. Anil Earnest",
            "Dr. Anil Kumar V",
            "Dr. Ashapurna Marndi",
            "Dr. Ashish",
            "Dr. CP Lakshmikanthan",
            "Dr. Dileep Kumar Shetty",
            "Dr. E Rajalakshmi",
            "Dr. G. Chiranjeevi Vivek",
            "Dr. Gayathri R",
            "Dr. Gopal Krishna Patra",
            "Dr. Gyanendranath Mohapatra",
            "Dr. Imtiyaz Ahmed Parvez",
            "Dr. K C Gouda",
            "Dr. K Rajendran",
            "Dr. Kanike Raghavendra Prasad Babu",
            "Dr. Kantha Rao Bhimala",
            "Dr. Karnan A",
            "Dr. Kuldeep Singh Yadav",
            "Dr. Nagarathna R.",
            "Dr. Neha",
            "Dr. Pousali Mukherjee",
            "Dr. Pranita Baro",
            "Dr. Prasanna Konatham",
            "Dr. Rakesh V",
            "Dr. Sajani Surendran",
            "Dr. Samiran Ghosh",
            "Dr. Sangeetha S",
            "Dr. Sithartha Muthu Vijayan",
            "Dr. Suribabu Donupudi",
            "Dr. Usha K Hasyagar",
            "Dr. V Senthilkumar",
            "Dr. Vivekananda Hazra",
            "Gugulothu Srilatha",
            "Gutta Jahnavi",
            "Manish Kumar",
            "Md Talib Hasan Ansari",
            "Mithun Babu N",
            "Pankaj Saini",
            "Pavithra N.R.",
            "Rakesh Asery",
            "Sanjeev Ekka",
            "Swapnil Burungale",
            "Zuber Khan"]

    return render(request, 'dashboard.html', {
        'page_obj':    page_obj,
        'stats':       stats,
        'active_tab':  active_tab,
        'q':           q,
        'scheme':      scheme,
        'area':        area,
        'areas':       areas,
        'tab_items':   TAB_ITEMS,
        'projects':    projects,  # <-- Passed to the template!
        'guides':      available_guides,  # <-- Here is the new addition!
        'month':       month, # 👈 NEW: Send it to the HTML
    })


# ═══════════════════════════════════════════════════════════════
# APPLICATION DETAIL
# ═══════════════════════════════════════════════════════════════

@portal_login_required
def portal_application_detail(request, app_id):
    app = get_object_or_404(Application, pk=app_id)
    return render(request, 'portal/application_detail.html', {'app': app})


# ═══════════════════════════════════════════════════════════════
# STATUS UPDATE  (POST only, AJAX-friendly)
# ═══════════════════════════════════════════════════════════════

@portal_login_required
@require_POST
def portal_update_status(request, app_id):
    app        = get_object_or_404(Application, pk=app_id)
    new_status = request.POST.get('status', '').strip()
    notes      = request.POST.get('admin_notes', '').strip()

    valid_statuses = {'Pending', 'Accepted', 'Rejected'}
    if new_status not in valid_statuses:
        messages.error(request, 'Invalid status value.')
        return redirect(f'/application/{app_id}/')

    app.status      = new_status
    app.admin_notes = notes
    app.reviewed_by = request.user
    app.reviewed_at = timezone.now()
    app.save(update_fields=['status', 'admin_notes', 'reviewed_by', 'reviewed_at'])

    messages.success(
        request,
        f'Application #{app.id} ({app.full_name}) marked as {new_status}.'
    )

    # Redirect back to referring tab or dashboard
    next_url = request.POST.get('next') or '/dashboard/'
    return redirect(next_url)


# ═══════════════════════════════════════════════════════════════
# DELETE APPLICATION  (SuperAdmin only)
# ═══════════════════════════════════════════════════════════════

@superadmin_required
@require_POST
def portal_delete_application(request, app_id):
    app = get_object_or_404(Application, pk=app_id)
    name = app.full_name
    app.delete()
    messages.success(request, f'Application from {name} has been deleted.')
    return redirect('/dashboard/?tab=all')


# ═══════════════════════════════════════════════════════════════
# EXPORT (portal versions — respect current tab/filter)
# ═══════════════════════════════════════════════════════════════

@portal_login_required
def portal_export_pdf_summary(request):
    """Full PDF summary of applications matching the CSV layout in A4 Landscape."""
    status_filter = request.GET.get('tab', '')
    month_filter  = request.GET.get('month', '')
    q             = request.GET.get('q', '').strip()
    scheme        = request.GET.get('scheme', '').strip()
    area          = request.GET.get('area', '').strip()

    # 1. Grab the exact same filtered queryset as the dashboard/CSV
    qs = Application.objects.all().order_by('-created_at')
    if status_filter in ('pending', 'accepted', 'rejected'):
        qs = qs.filter(status=status_filter.capitalize())
    if month_filter:
        qs = qs.filter(created_at__month=month_filter)
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) | Q(email__icontains=q) |
            Q(institute_name__icontains=q) | Q(area_of_interest__icontains=q)
        )
    if scheme:
        qs = qs.filter(scheme=scheme)
    if area:
        qs = qs.filter(area_of_interest=area)

    # 2. Setup the PDF response in landscape mode
    response = HttpResponse(content_type='application/pdf')
    label = status_filter or 'all'
    response['Content-Disposition'] = f'attachment; filename="spark_{label}_report.pdf"'

    # Creative document container using A4 Landscape
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10*mm, leftMargin=10*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )
    
    # 3. Typography Styles Setup
    styles = getSampleStyleSheet()
    
    # Customize standard styles for narrow column rows
    style_header = ParagraphStyle(
        'PDFHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9,
        textColor=colors.white, alignment=TA_CENTER
    )
    style_cell = ParagraphStyle(
        'PDFCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9,
        leading=10, textColor=colors.HexColor('#222222')
    )
    style_title = ParagraphStyle(
        'PDFTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=20,
        leading=20, textColor=colors.HexColor('#003366'),
        spaceAfter=10
    )

    story = []
    
    # Document Title Header banner text
    title_text = f"SPARK Admin Portal — {label.upper()} Applications Summary"
    if month_filter:
        import calendar
        title_text += f" ({calendar.month_name[int(month_filter)]})"
    story.append(Paragraph(title_text, style_title))
    
    # 4. Define Table Headers matching the CSV exactly
    headers = [
        Paragraph('App.ID', style_header),
        Paragraph('Student Name', style_header),
        Paragraph('Course of Study', style_header),
        Paragraph('Name of University/Institute', style_header),
        Paragraph('Project Start Date<br/>(Duration)', style_header),
        Paragraph('CSIR-4PI Guide', style_header),
        Paragraph('University Guide', style_header),
        Paragraph('SPARK Recommendation', style_header),
        Paragraph('Mode of attendance', style_header)
    ]
    
    table_data = [headers]

    # 5. Populate Data Rows exactly like CSV export
    for a in qs:
        # Format Course string
        course = a.course_name
        if hasattr(a, 'specialization') and a.specialization:
            course = f"{course} ({a.specialization})"

        # Format Start Date & Duration
        date_str = a.internship_from.strftime('%d/%m/%Y') if a.internship_from else '---'
        duration_str = f"({a.duration_months:02d} M)" if a.duration_months else '(---)'
        start_date_formatted = f"{date_str}\n{duration_str}"

        # Recommendation translation logic
        if a.admin_notes:
            recommendation = a.admin_notes
        elif a.status == 'Accepted':
            recommendation = 'Recommended'
        elif a.status == 'Rejected':
            recommendation = 'Not Recommended'
        else:
            recommendation = 'Not Recommended'

        # Force long texts inside Paragraph objects to ensure automatic text-wrapping
        row = [
            Paragraph(str(a.id), style_cell),
            Paragraph(f"<b>{a.full_name}</b>", style_cell),
            Paragraph(course, style_cell),
            Paragraph(a.institute_name, style_cell),
            Paragraph(start_date_formatted, style_cell),
            Paragraph(a.csir_guide_name or '---', style_cell),
            Paragraph(a.guide_name or '---', style_cell),
            Paragraph(recommendation, style_cell)
        ]
        table_data.append(row)

    # 6. Strict Column Width Allocation to fully fit A4 Landscape (Total printable width = 277mm)
    # AppID, Name, Course, University, Dates, CSIRGuide, UniGuide, Mode, Rec
    col_widths = [14*mm, 40*mm, 38*mm, 45*mm, 28*mm, 32*mm, 32*mm, 18*mm, 30*mm]
    
    # Build Table
    summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # 7. Apply visual formatting styles
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')), # Dark Blue top bar
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')), # Soft grey lines
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(summary_table)
    
    # Build Document
    doc.build(story)
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

@portal_login_required
def portal_export_pdf_single(request, app_id):
    """Detailed single-application PDF — reuses existing logic."""
    from .views import export_pdf_single
    return export_pdf_single(request, app_id)


@portal_login_required
def portal_export_csv(request):
    """CSV export for current filtered set using the official recommendation format."""
    import csv as csv_module
    status_filter = request.GET.get('tab', '')
    
    # Grab the filtered applications just like before
    qs = Application.objects.all().order_by('-created_at')
    if status_filter in ('pending', 'accepted', 'rejected'):
        qs = qs.filter(status=status_filter.capitalize())

    response = HttpResponse(content_type='text/csv')
    label = status_filter or 'all'
    response['Content-Disposition'] = f'attachment; filename="spark_{label}_report.csv"'
    writer = csv_module.writer(response)
    
    # 1. Write the official headers from the spreadsheet
    writer.writerow([
        'App.ID',
        'Student Name',
        'Course of Study',
        'Name of The University/Institute',
        'Project start date (dd/mm/yyyy) (duration of month)',
        'CSIR-4PI Guide',
        'University/ Institute Guide',
        'SPARK Recommendation',
        'Mode of attendance'
    ])
    
    # 2. Format and write the data
    for a in qs:
        # Format Course: e.g., "BE/Btech (Civil Engineering)"
        course = a.course_name
        if a.specialization:
            course = f"{course} ({a.specialization})"

        # Format Date & Duration: e.g., "20/05/2026(03)"
        date_str = a.internship_from.strftime('%d/%m/%Y') if a.internship_from else '---'
        duration_str = f"({a.duration_months:02d})" if a.duration_months else '(---)'
        start_date_formatted = f"{date_str}{duration_str}"

        # Recommendation Logic (Defaults based on current status)
        if a.admin_notes:
            recommendation = a.admin_notes
        elif a.status == 'Accepted':
            recommendation = 'Recommended'
        elif a.status == 'Rejected':
            recommendation = 'Not Recommended'
        else:
            recommendation = 'Not Recommended'

        writer.writerow([
            a.id,
            f"{a.full_name} *",  # Adds the asterisk to the name
            course,
            a.institute_name,
            start_date_formatted,
            a.csir_guide_name or '---',
            a.guide_name or '---',
            recommendation,
            a.attendance_mode or '---'
        ])
        
    return response


# ═══════════════════════════════════════════════════════════════
# USER MANAGEMENT  (SuperAdmin only)
# ═══════════════════════════════════════════════════════════════

@superadmin_required
def portal_users(request):
    reviewer_group, _ = Group.objects.get_or_create(name='Reviewer')
    reviewers   = User.objects.filter(groups=reviewer_group).order_by('username')
    superadmins = User.objects.filter(is_superuser=True).order_by('username')
    return render(request, 'portal/users.html', {
        'reviewers':   reviewers,
        'superadmins': superadmins,
    })


@superadmin_required
@require_POST
def portal_create_reviewer(request):
    username   = request.POST.get('username', '').strip()
    password   = request.POST.get('password', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name  = request.POST.get('last_name', '').strip()
    email      = request.POST.get('email', '').strip()

    if not username or not password:
        messages.error(request, 'Username and password are required.')
        return redirect('/users/')

    if User.objects.filter(username=username).exists():
        messages.error(request, f'Username "{username}" already exists.')
        return redirect('/users/')

    user = User.objects.create_user(
        username=username, password=password,
        first_name=first_name, last_name=last_name, email=email,
    )
    reviewer_group, _ = Group.objects.get_or_create(name='Reviewer')
    user.groups.add(reviewer_group)
    messages.success(request, f'Reviewer account "{username}" created successfully.')
    return redirect('/users/')


@superadmin_required
@require_POST
def portal_remove_reviewer(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    reviewer_group = Group.objects.get(name='Reviewer')
    user.groups.remove(reviewer_group)
    messages.success(request, f'Reviewer access removed from "{user.username}".')
    return redirect('/users/')
