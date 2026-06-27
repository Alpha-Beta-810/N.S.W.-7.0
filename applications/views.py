import csv
import io
from collections import defaultdict
from datetime import timedelta

from .models import Application, Project  # Add Project here

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .forms import ApplicationForm
from .models import Application

AREA_CHOICES = [
    ('', '-- Select Area --'),
    ('AI/ML', 'AI/ML'),
    ('Climate and Environment Modelling', 'Climate and Environment Modelling'),
    ('Computational Mechanics Programme', 'Computational Mechanics Programme'),
    ('High Performance Computing and Cyber Security', 'High Performance Computing and Cyber Security'),
    ('Quantum computing', 'Quantum computing'),
    ('Smart Agritech', 'Smart Agritech'),
    
    
    ('Solid Earth Modelling Programme', 'Solid Earth Modelling Programme'),
    ('View of Earthquake Risk', 'View of Earthquake Risk'),
]


def home(request):
    areas = [c[1] for c in AREA_CHOICES if c[0]]
    return render(request, "home.html", {"areas": areas})


def apply(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/success/')
    else:
        form = ApplicationForm()
    return render(request, "apply.html", {"form": form})


def success(request):
    return render(request, "success.html")


def guidelines(request):
    accommodation = [
        'Kodihalli', 'Murugeshpalya', 'Jeevan Bhima Nagar', 'Domlur',
        'Thippasandra', 'Yemlur', 'Marthahalli', 'HAL', 'Indira Nagar',
    ]
    return render(request, "guidelines.html", {"accommodation": accommodation})


def projects(request):
    # 1. Pull all live projects from the database
    live_projects = Project.objects.all().order_by('area')
    
    # 2. Group them by area (just like your old code did!)
    grouped = defaultdict(list)
    for p in live_projects:
        grouped[p.area].append(p)
        
    # 3. Format it exactly how your HTML template expects it
    project_groups = [{"area": a, "projects": ps} for a, ps in grouped.items()]
    
    return render(request, "projects.html", {"project_groups": project_groups})


def contact(request):
    return render(request, "contact.html")


def forms_download(request):
    downloads = [
        {"name": "Joining Certificate (Project/Thesis)", "desc": "Signed by candidate, guide & HOD", "url": "/static/downloads/spark_attestation_th.doc"},
        {"name": "Joining Certificate (Internship)", "desc": "Signed by candidate & HOD", "url": "/static/downloads/spark_attestation_int.doc"},
        {"name": "Thesis Cover Page Format", "desc": "Required format for thesis submission", "url": "/static/downloads/thesis_coverpage.doc"},
        {"name": "No Due Form", "desc": "Submit along with thesis at relieving", "url": "/static/downloads/no_due_certificate.doc"},
        {"name": "SPARK Feedback Form", "desc": "Guidelines for Online Training Programme", "url": "/static/downloads/spark_feedback.pdf"},
        {"name": "SPARK Online Guidelines", "desc": "Guidelines for Online Training Programme", "url": "/static/downloads/spark_online_guidelines.pdf"},
    ]
    return render(request, "forms_download.html", {"downloads": downloads})
    
@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spark_applications.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Title', 'Name', 'DOB', 'Gender', 'Nationality',
        'Email', 'Mobile', 'Phone', 'City', 'State', 'Pincode',
        'Course', 'Institute Category', 'Institute', 'Department', 'Duration', 'CGPA',
        '10th %', '12th %', 'Highest Degree',
        'Scheme', 'From', 'To', 'Duration (mo)', 'Area of Interest',
        'Guide Name', 'Guide Designation', 'Guide Dept', 'Guide Email', 'Guide Phone',
        'CSIR Guide', 'Statement', 'Applied On',
    ])
    for a in Application.objects.all().order_by('-created_at'):
        writer.writerow([
            a.id, a.title, a.full_name, a.dob, a.gender, a.nationality,
            a.email, a.mobile, a.phone, a.city, a.state, a.pincode,
            a.course_name, a.institute_category, a.institute_name, a.department,
            a.course_duration, a.cgpa,
            a.tenth_percentage, a.twelfth_percentage, a.highest_degree,
            a.scheme, a.internship_from, a.internship_to, a.duration_months,
            a.area_of_interest,
            a.guide_name, a.guide_designation, a.guide_department,
            a.guide_email, a.guide_phone, a.csir_guide_name,
            a.statement, a.created_at.strftime('%Y-%m-%d'),
        ])
    return response

@login_required
def export_minimal_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spark_applications_minimal.csv"'
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow([
        'Application ID', 
        'Student Name', 
        'Course of Study', 
        'University/Institute Name', 
        'Project Start Date', 
        'CSIR-4PI Guide', 
        'University/Institute Guide'
    ])

    # Fetch and write the data rows
    for a in Application.objects.all().order_by('-created_at'):
        csir_guide = a.csir_guide_name if a.csir_guide_name else "None"
        
        writer.writerow([
            a.id,
            a.full_name,
            a.course_name,
            a.institute_name,
            a.internship_from,
            csir_guide,
            a.guide_name
        ])

    return response


@login_required
def export_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=18*mm, bottomMargin=18*mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=14,
        spaceAfter=4,
        textColor=colors.HexColor('#003366'),
        alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        wordWrap='CJK',
    )
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    )

    story = []
    story.append(Paragraph("CSIR-4PI SPARK Programme — Applications Summary", title_style))
    story.append(Paragraph(
        f"Generated on {timezone.now().strftime('%d %B %Y, %I:%M %p')}",
        sub_style,
    ))

    headers = [
        Paragraph("App. ID", header_style),
        Paragraph("Student Name", header_style),
        Paragraph("Course of Study", header_style),
        Paragraph("University / Institute", header_style),
        Paragraph("Project Start Date", header_style),
        Paragraph("CSIR-4PI Guide", header_style),
        Paragraph("University / Institute Guide", header_style),
    ]

    col_widths = [18*mm, 42*mm, 38*mm, 62*mm, 30*mm, 44*mm, 50*mm]

    data = [headers]
    for app in Application.objects.all().order_by('-created_at'):
        start_date = app.internship_from.strftime('%d %b %Y') if app.internship_from else '—'
        data.append([
            Paragraph(str(app.id), ParagraphStyle('c', parent=cell_style, alignment=TA_CENTER)),
            Paragraph(f"{app.title} {app.full_name}", cell_style),
            Paragraph(app.course_name or '—', cell_style),
            Paragraph(app.institute_name or '—', cell_style),
            Paragraph(start_date, ParagraphStyle('c', parent=cell_style, alignment=TA_CENTER)),
            Paragraph(app.csir_guide_name or '—', cell_style),
            Paragraph(app.guide_name or '—', cell_style),
        ])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING',    (0, 0), (-1, 0), 6),
        # Data rows
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 7.5),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
        # Alternating row colours
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EEF3FA')]),
        # Grid
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#CCCCCC')),
        ('LINEBELOW',     (0, 0), (-1, 0), 1, colors.HexColor('#001f4d')),
    ]))

    story.append(table)
    doc.build(story)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="spark_applications_summary.pdf"'
    return response


@login_required
def export_pdf_single(request, app_id):
    """Generate a detailed PDF summary for a single application."""
    from django.shortcuts import get_object_or_404
    app = get_object_or_404(Application, pk=app_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle', parent=styles['Title'],
        fontSize=14, spaceAfter=4,
        textColor=colors.HexColor('#003366'), alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        'SubTitle', parent=styles['Normal'],
        fontSize=8, spaceAfter=12,
        textColor=colors.grey, alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        'Section', parent=styles['Normal'],
        fontSize=10, spaceBefore=10, spaceAfter=4,
        textColor=colors.white, fontName='Helvetica-Bold',
        backColor=colors.HexColor('#003366'),
        leftIndent=4, leading=14,
    )
    cell_label = ParagraphStyle(
        'CellLabel', parent=styles['Normal'],
        fontSize=8.5, textColor=colors.HexColor('#555555'), fontName='Helvetica-Bold',
    )
    cell_value = ParagraphStyle(
        'CellValue', parent=styles['Normal'],
        fontSize=8.5, textColor=colors.black,
    )

    def row(label, value):
        return [Paragraph(label, cell_label), Paragraph(str(value) if value else '—', cell_value)]

    story = []
    story.append(Paragraph("CSIR-4PI SPARK Programme", title_style))
    story.append(Paragraph("Application Detail Summary", title_style))
    story.append(Paragraph(
        f"Application ID: {app.id}  |  Generated on {timezone.now().strftime('%d %B %Y, %I:%M %p')}",
        sub_style,
    ))

    def section_table(title, rows_data):
        story.append(Paragraph(f"  {title}", section_style))
        t = Table(rows_data, colWidths=[65*mm, 105*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F4FA')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ]))
        story.append(t)
        story.append(Spacer(1, 4))

    # Personal
    section_table("Personal Details", [
        row("Name", f"{app.title} {app.full_name}"),
        row("Date of Birth", str(app.dob) if app.dob else '—'),
        row("Gender", app.gender),
        row("Nationality", app.nationality),
        row("Email", app.email),
        row("Mobile", app.mobile),
        row("Phone", app.phone or '—'),
        row("Address", f"{app.address}, {app.city}, {app.state} – {app.pincode}"),
    ])

    # Current Course
    section_table("Current Course Details", [
        row("Institute", app.institute_name),
        row("Institute Category", app.institute_category),
        row("Department", app.department),
        row("Specialization", app.specialization or '—'),
        row("Course Name", app.course_name),
        row("Course Duration", f"{app.course_duration} Year(s)"),
        row("CGPA / Marks", str(app.cgpa) if app.cgpa is not None else '—'),
    ])

    # Previous Academic
    section_table("Previous Academic Details", [
        row("Highest Degree", app.highest_degree or '—'),
        row("Prev. Specialization", app.prev_specialization or '—'),
        row("Prev. Institute", app.prev_institute or '—'),
        row("Prev. Department", app.prev_department or '—'),
        row("Prev. CGPA / Marks", str(app.prev_cgpa) if app.prev_cgpa is not None else '—'),
        row("10th Percentage", f"{app.tenth_percentage}%"),
        row("12th Percentage", f"{app.twelfth_percentage}%"),
    ])

    # Project Info
    from_date = app.internship_from.strftime('%d %b %Y') if app.internship_from else '—'
    to_date   = app.internship_to.strftime('%d %b %Y') if app.internship_to else '—'
    section_table("Project / Thesis Information", [
        row("Scheme", app.scheme or '—'),
        row("Area of Interest", app.area_of_interest or '—'),
        row("From", from_date),
        row("To", to_date),
        row("Duration (Months)", str(app.duration_months) if app.duration_months else '—'),
        row("Statement of Purpose", app.statement or '—'),
        row("Relevant Experience", app.experience or '—'),
        row("Previous Project Work", app.project_interest or '—'),
    ])

    # Guide
    section_table("Guide / HOD Details (University / Institute)", [
        row("Guide Name", app.guide_name or '—'),
        row("Designation", app.guide_designation or '—'),
        row("Department", app.guide_department or '—'),
        row("Email", app.guide_email or '—'),
        row("Phone", app.guide_phone or '—'),
        row("CSIR-4PI Guide", app.csir_guide_name or '—'),
    ])

    # Other
    section_table("Other Information", [
        row("Other Relevant Info", app.other_info or '—'),
        row("Resume Uploaded", "Yes" if app.resume else "No"),
        row("Applied On", app.created_at.strftime('%d %B %Y, %I:%M %p')),
    ])

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    safe_name = f"application_{app.id}_{app.full_name.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{safe_name}"'
    return response


def user_login(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == "POST":
        user = authenticate(request,
                            username=request.POST.get("username"),
                            password=request.POST.get("password"))
        if user is not None:
            login(request, user)
            return redirect(next_url)
        return render(request, "login.html", {"error": "Invalid credentials", "next": next_url})
    return render(request, "login.html", {"next": next_url})


def user_logout(request):
    logout(request)
    return redirect("/")
