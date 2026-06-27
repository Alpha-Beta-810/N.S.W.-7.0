from django import forms
from datetime import date
from .models import (Application, TITLE_CHOICES, COURSE_CHOICES,
                     INSTITUTE_CATEGORY_CHOICES, COURSE_DURATION_CHOICES,
                     HIGHEST_DEGREE_CHOICES, SCHEME_CHOICES,
                     AREA_OF_INTEREST_CHOICES)

# Defines the options for the score type dropdowns used in the form.
SCORE_TYPE_CHOICES = [
    ('cgpa',  'CGPA (out of 10)'),
    ('marks', 'Marks / Percentage (out of 100)'),
]

class ApplicationForm(forms.ModelForm):
    """
    ModelForm tied to the Application model. It automatically creates form fields
    based on the model, but we override widgets and add custom validation.
    """

    # ── Non-model fields ──────────────────────────────────────────────────────
    # These fields exist only in the form for UI/logic purposes and are not 
    # directly saved to the database model automatically.
    
    score_type = forms.ChoiceField(
        choices=SCORE_TYPE_CHOICES, label='Score Type (Current)',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_score_type'}),
    )
    prev_score_type = forms.ChoiceField(
        choices=SCORE_TYPE_CHOICES, label='Score Type (Previous)',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_prev_score_type'}),
    )

    # A required checkbox forcing the user to agree before submission.
    declaration = forms.BooleanField(
        required=True,
        label=('I hereby declare that the information given above is correct to '
               'the best of my knowledge and belief. I am aware that if any part '
               'of the data / information submitted is found to be false or '
               'misleading, the candidature can be rejected at any stage.'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_declaration'}),
        error_messages={'required': 'You must accept the declaration to submit.'},
    )

    class Meta:
        model  = Application
        fields = '__all__' # Includes all fields from the Application model

        # The widgets dictionary allows us to inject CSS classes (like Bootstrap's 
        # 'form-control') and HTML attributes (like 'maxlength' or 'id') directly 
        # into the rendered HTML inputs.
        widgets = {
            # ── Personal ──────────────────────────────────────────────
            'title': forms.Select(
                choices=TITLE_CHOICES,
                attrs={'class': 'form-select', 'style': 'width:90px'}
            ),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(
                choices=[('', '-- Gender --'), ('Male', 'Male'),
                         ('Female', 'Female'), ('Other', 'Other')],
                attrs={'class': 'form-select'},
            ),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city':    forms.TextInput(attrs={'class': 'form-control'}),
            'state':   forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control', 'maxlength': '6',
                'inputmode': 'numeric', 'id': 'id_pincode',
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'maxlength': '15',
                'placeholder': 'e.g. 08025XXXXXX', 'id': 'id_phone',
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control', 'maxlength': '10',
                'inputmode': 'numeric', 'id': 'id_mobile',
                'placeholder': 'e.g. 9035XXXXXX',
            }),

            # ── Current Academic ──────────────────────────────────────
            # Note: Fields are ordered here to match the requested visual order 
            # (institute details first, then course details).
            'institute_name': forms.TextInput(attrs={'class': 'form-control'}),
            'institute_category': forms.Select(
                choices=INSTITUTE_CATEGORY_CHOICES, attrs={'class': 'form-select'},
            ),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'course_name': forms.Select(
                choices=COURSE_CHOICES,
                attrs={'class': 'form-select', 'id': 'id_course_name'},
            ),
            'course_duration': forms.Select(
                choices=COURSE_DURATION_CHOICES, attrs={'class': 'form-select'},
            ),
            'course_other': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Please specify',
                'id': 'id_course_other',
            }),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'institute_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cgpa': forms.NumberInput(attrs={
                'class': 'form-control', 'id': 'id_cgpa',
                'step': '0.01', 'min': '0', 'max': '10',
            }),

            # ── Previous Academic ─────────────────────────────────────
            'tenth_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 'id': 'id_tenth',
                'step': '0.01', 'min': '0', 'max': '100',
            }),
            'twelfth_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 'id': 'id_twelfth',
                'step': '0.01', 'min': '0', 'max': '100',
            }),
            'highest_degree': forms.Select(
                choices=HIGHEST_DEGREE_CHOICES, attrs={'class': 'form-select'},
            ),
            'prev_specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'prev_institute_category': forms.Select(
                choices=INSTITUTE_CATEGORY_CHOICES, attrs={'class': 'form-select'},
            ),
            'prev_institute': forms.TextInput(attrs={'class': 'form-control'}),
            'prev_department': forms.TextInput(attrs={'class': 'form-control'}),
            'prev_institute_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prev_cgpa': forms.NumberInput(attrs={
                'class': 'form-control', 'id': 'id_prev_cgpa',
                'step': '0.01', 'min': '0', 'max': '10',
            }),

            # ── Project / Scheme ──────────────────────────────────────
            'scheme': forms.Select(
                choices=SCHEME_CHOICES,
                attrs={'class': 'form-select', 'id': 'id_scheme'},
            ),
            'internship_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'internship_to':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duration_months': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'max': '3', 'placeholder': 'Max 3',
            }),
            'area_of_interest': forms.Select(
                choices=AREA_OF_INTEREST_CHOICES,
                attrs={'class': 'form-select', 'id': 'id_area_of_interest'},
            ),
            'area_other': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Please specify',
                'id': 'id_area_other',
            }),
            'project_interest': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'statement':        forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'experience':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'other_info':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            # ── University Guide ──────────────────────────────────────
            'guide_name':        forms.TextInput(attrs={'class': 'form-control'}),
            'guide_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'guide_department':  forms.TextInput(attrs={'class': 'form-control'}),
            'guide_email':       forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_guide_email'}),
            'guide_phone':       forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 08025XXXXXX / 090357XXXXX',
            }),
            'csir_guide_name': forms.TextInput(attrs={'class': 'form-control'}),

            # ── Resume ────────────────────────────────────────────────
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    # ── Server-side validation ────────────────────────────────────────

    def clean(self):
        """
        The master clean method. Used for cross-field validation where the validity 
        of one field depends on the value of another field.
        """
        # Call the parent's clean method to get the dictionary of already-cleaned data
        cleaned_data = super().clean()
        
        duration = cleaned_data.get('duration_months')
        course = cleaned_data.get('course_name')
        
        if duration:
            # Rule 1: Specific courses must have a duration between 2 and 6 months
            if course in ['BE/BTech', 'MSc', 'MCA']:
                if duration < 2 or duration > 6:
                    # add_error attaches the error to a specific field in the UI
                    self.add_error('duration_months', "Duration must be 2–6 months")
            
            # Rule 2: PhD must be between 2 to 12 months
            if course == 'PhD':
                if duration < 2 or duration > 12:
                    self.add_error('duration_months', "PhD duration must be 12 months")
                    
        return cleaned_data

    # ── Single Field Validations ──────────────────────────────────────
    # Django automatically calls methods named clean_<fieldname>() to validate 
    # individual fields. If a validation fails, it raises a ValidationError.

    def clean_mobile(self):
        v = self.cleaned_data.get('mobile', '').strip()
        if not v:
            raise forms.ValidationError("Mobile number is required.")
        if not v.isdigit() or len(v) != 10:
            raise forms.ValidationError("Must be exactly 10 digits.")
        return v

    def clean_pincode(self):
        v = self.cleaned_data.get('pincode', '').strip()
        if not v:
            raise forms.ValidationError("Pincode is required.")
        if not v.isdigit() or len(v) != 6:
            raise forms.ValidationError("Must be exactly 6 digits.")
        return v

    def clean_phone(self):
        v = self.cleaned_data.get('phone', '').strip()
        if not v:
            raise forms.ValidationError("Phone number is required.")
        # Strip common formatting characters to check if the core is numeric
        digits_only = v.replace(' ', '').replace('-', '')
        if not digits_only.isdigit():
            raise forms.ValidationError("Phone must contain digits only.")
        return v

    def clean_tenth_percentage(self):
        v = self.cleaned_data.get('tenth_percentage')
        if v is None:
            raise forms.ValidationError("Required.")
        if not (0 <= v <= 100):
            raise forms.ValidationError("Must be between 0 and 100.")
        return v

    def clean_twelfth_percentage(self):
        v = self.cleaned_data.get('twelfth_percentage')
        if v is None:
            raise forms.ValidationError("Required.")
        if not (0 <= v <= 100):
            raise forms.ValidationError("Must be between 0 and 100.")
        return v

    def clean_cgpa(self):
        value = self.cleaned_data.get('cgpa')
        # We access self.data to get the raw input from the form submission to 
        # check which score type the user selected.
        score_type = self.data.get('score_type', 'cgpa')
        
        if value is None:
            raise forms.ValidationError("Required.")
        
        # Validate based on the chosen scale
        if score_type == 'cgpa':
            if not (0 <= value <= 10.0):
                raise forms.ValidationError("CGPA must be 0.00 – 10.00.")
        else:
            if not (0 <= value <= 100.0):
                raise forms.ValidationError("Marks must be 0.00 – 100.00.")
        return value

    def clean_prev_cgpa(self):
        value = self.cleaned_data.get('prev_cgpa')
        if value is None:
            return value # Optional field, so return None if empty
            
        score_type = self.data.get('prev_score_type', 'cgpa')
        if score_type == 'cgpa':
            if not (0 <= value <= 10.0):
                raise forms.ValidationError("CGPA must be 0.00 – 10.00.")
        else:
            if not (0 <= value <= 100.0):
                raise forms.ValidationError("Marks must be 0.00 – 100.00.")
        return value

    def clean_duration_months(self):
        v = self.cleaned_data.get('duration_months')
        if v is not None and v > 12:
            raise forms.ValidationError("Maximum duration is 12 months.")
        return v

    def clean_resume(self):
        f = self.cleaned_data.get('resume')
        if f:
            # Enforce file type
            if not f.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            # Enforce file size (2MB max)
            if f.size > 2 * 1024 * 1024:
                raise forms.ValidationError("File must be under 2 MB.")
        return f
        
    """def clean_internship_from(self):
        v = self.cleaned_data.get('internship_from')
        if v and v < date.today():
            raise forms.ValidationError("Start date cannot be in the past.")
        return v"""

    def clean_internship_to(self):
        v = self.cleaned_data.get('internship_to')
        from_date = self.cleaned_data.get('internship_from')
        
        if v and v < date.today():
            raise forms.ValidationError("End date cannot be in the past.")
            
        if v and from_date and v <= from_date:
            raise forms.ValidationError("End date must be after the start date.")
            
        return v
