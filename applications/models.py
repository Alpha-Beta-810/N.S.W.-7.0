from django.db import models
from django.contrib.auth.models import User

TITLE_CHOICES = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms')]

COURSE_CHOICES = [
    ('', '-- Select Course --'),
    ('BE/BTech', 'BE / B.Tech'),
    ('BS', 'B.S'),
    ('BSc', 'B.Sc'),
    ('MCA', 'M.C.A'),
    ('ME/MTech', 'ME / M.Tech'),
    ('MPhil', 'M.Phil'),
    ('MS', 'M.S'),
    ('MSc', 'M.Sc'),
    ('PhD', 'Ph.D'),
    ('Others', 'Others'),
]

INSTITUTE_CATEGORY_CHOICES = [
    ('', '-- Select Category --'),
    ('IISc', 'IISc'),
    ('IISER', 'IISER'),
    ('IIT', 'IIT'),
    ('NIT', 'NIT'),
    ('University', 'University'),
    ('OTHERS', 'Others'),
]

COURSE_DURATION_CHOICES = [
    ('1', '1 Year'),
    ('2', '2 Years'),
    ('3', '3 Years'),
    ('4', '4 Years'),
    ('5', '5 Years'),
]

HIGHEST_DEGREE_CHOICES = [
    ('', '-- Select Degree --'),
    ('BS', 'B.S'),
    ('BSc', 'B.Sc'),
    ('BE/BTech', 'BE / B.Tech'),
    ('ME/MTech', 'ME / M.Tech'),
    ('MS', 'M.Sc'),
    ('MSc', 'M.S'),
    ('MCA', 'M.C.A'),
    ('MPhil', 'M.Phil'),
    ('PhD', 'Ph.D'),
    ('PUC', 'PUC'),
    ('Diploma', 'Diploma'),
    ('Others', 'Others'),
]

SCHEME_CHOICES = [
    ('', '-- Select Scheme --'),
    ('Project/Thesis', 'Project / Thesis'),
    ('Internship', 'Internship'),
]

AREA_OF_INTEREST_CHOICES = [
    ('', '-- Select Area --'),
    ('Climate and Environmental Modelling Programme', 'Climate and Environmental Modelling Programme'),
    ('Carbon Cycle and Ocean Modelling', 'Carbon Cycle and Ocean Modelling'),
    ('Computational Mechanics Programme', 'Computational Mechanics Programme'),
    ('High Performance Computing', 'High Performance Computing'),
    ('Multiscale Modelling and Simulation', 'Multiscale Modelling and Simulation'),
    ('Solid Earth Modelling Programme', 'Solid Earth Modelling Programme'),
    
    # --- NEW OPTIONS ADDED HERE ---
    ('Robotics', 'Robotics'),
    ('Development of LLMs/VLMs', 'Development of LLMs/VLMs'),
    ('High performance computing', 'High performance computing'),
    ('Cyber Security', 'Cyber Security'),
    ('Catastrophe modelling', 'Catastrophe modelling'),
    ('AI-ML applications for earthquake modelling', 'AI-ML applications for earthquake modelling'),
    ('Quantum Technologies', 'Quantum Technologies'),
    ('Agentic AI', 'Agentic AI'),
    # ------------------------------
    
    ('Others', 'Others'),
]

APPLICATION_STATUS_CHOICES = [
    ('Pending',  'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
]

class Application(models.Model):
    # ── Personal Info ──────────────────────────────────────────────────
    title       = models.CharField(max_length=5, choices=TITLE_CHOICES, default='Mr')
    full_name   = models.CharField(max_length=200)
    dob         = models.DateField()
    gender      = models.CharField(max_length=10)
    nationality = models.CharField(max_length=100, default='Indian')

    address     = models.TextField()
    city        = models.CharField(max_length=100)
    state       = models.CharField(max_length=100)
    pincode     = models.CharField(max_length=10)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20)
    mobile      = models.CharField(max_length=20)

    # ── Current Academic ───────────────────────────────────────────────
    course_name         = models.CharField(max_length=200)
    course_other        = models.CharField(max_length=200, blank=True)
    specialization      = models.CharField(max_length=200)
    institute_category  = models.CharField(max_length=50, blank=True)
    institute_name      = models.CharField(max_length=200)
    department          = models.CharField(max_length=200)
    institute_address   = models.TextField()
    course_duration     = models.CharField(max_length=20)
    cgpa                = models.FloatField()

    # ── Previous Academic ──────────────────────────────────────────────
    tenth_percentage    = models.FloatField()
    twelfth_percentage  = models.FloatField()
    highest_degree      = models.CharField(max_length=200)
    prev_specialization = models.CharField(max_length=200, blank=True)
    prev_institute_category = models.CharField(max_length=50, blank=True)
    prev_institute      = models.CharField(max_length=200, blank=True)
    prev_department     = models.CharField(max_length=200, blank=True)
    prev_institute_address = models.TextField(blank=True)
    prev_cgpa           = models.FloatField(null=True, blank=True)

    # ── Project / Internship ───────────────────────────────────────────
    scheme              = models.CharField(max_length=30, choices=SCHEME_CHOICES, default='Internship')
    internship_from     = models.DateField(null=True, blank=True)
    internship_to       = models.DateField(null=True, blank=True)
    duration_months     = models.PositiveSmallIntegerField(null=True, blank=True)
    area_of_interest    = models.CharField(max_length=200)
    area_other          = models.CharField(max_length=200, blank=True)

    # ── University Guide ───────────────────────────────────────────────
    guide_name          = models.CharField(max_length=200)
    guide_designation   = models.CharField(max_length=200)
    guide_department    = models.CharField(max_length=200)
    guide_email         = models.EmailField()
    guide_phone         = models.CharField(max_length=20)
    csir_guide_name     = models.CharField(max_length=200, blank=True)

    # ── Other ──────────────────────────────────────────────────────────
    project_interest    = models.TextField(blank=True)
    statement           = models.TextField()
    experience          = models.TextField(blank=True)
    other_info          = models.TextField(blank=True)

    # ✅ Resume upload (column already exists in DB from migration 0004)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    # ── Admin / Workflow ──────────────────────────────────────
    status      = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='Pending')
    admin_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_apps')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    attendance_mode = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.title} {self.full_name}"
        
class Project(models.Model):
    area = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    email = models.CharField(max_length=255)

    def __str__(self):
        return self.title
