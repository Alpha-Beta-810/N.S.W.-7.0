# N.S.W-7.0 (New Spark Website 7) : A Prototye Academic Research Application Portal

A comprehensive, Django-based web application prototype designed to manage student applications on an organizational level.
This portal allows students to apply for internships and project/thesis work under various scientists, while providing administrators with a robust dashboard to track, review, and export applications.
A robust, Django-based web application engineered to manage, review, and process academic internship and thesis applications.
Built with a focus on Role-Based Access Control (RBAC), automated document generation, and secure data handling, this platform provides a seamless bridge between applicants and reviewing principal investigators (PIs).

## 🚀 Features

### For Students (Applicants)
* **Dynamic Application Form**: A responsive, multi-section form capturing personal, academic, and project details.
* **Smart Validation**: 
  * Client-side (JS) and Server-side (Django) validation.
  * Auto-calculated project durations based on selected dates.
  * Conditional logic for PhD vs. UG/PG degree duration caps (2-6 months vs. up to 12 months).
  * Future-date restrictions to prevent backdated applications.
* **File Uploads**: Secure PDF resume uploads with size (Max 2MB) and type restrictions.

### For Administrators (Reviewers & Superusers)
* **Role-Based Access Control (RBAC)**: Secure portal routes restricted to Superadmins and designated 'Reviewer' groups.
* **Analytics Dashboard**: Real-time statistics showing total applications, recent applications, and breakdowns by scheme.
* **Application Review Workflow**: A custom admin portal to mark applications as `Pending`, `Accepted`, or `Rejected` with internal review notes.
* **Data Exporting**:
  * **Full CSV Export**: Downloads all application data fields.
  * **Minimal CSV Export**: Downloads a lightweight, focused list for quick overviews.
  * **PDF Generation**: Auto-generates beautifully formatted PDF summaries of all applications or single detailed applications using `reportlab`.

## 🛠️ Tech Stack

* **Backend**: Python 3, Django 5+
* **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5
* **Database**: SQLite (Default) / PostgreSQL (Ready)
* **PDF Generation**: ReportLab
* **Icons**: Bootstrap Icons

## ⚙️ Installation & Setup

### Prerequisites
Make sure you have Python 3.9+ and `pip` installed on your machine.

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/spark-application-portal.git](https://github.com/yourusername/spark-application-portal.git)
cd spark-application-portal

```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

### 3. Install Dependencies

*(Make sure to create a `requirements.txt` file with Django and reportlab if you haven't already).*

```bash
pip install django reportlab

```

### 4. Run Database Migrations

Apply the database schema, including the custom Application models and RBAC fields.

```bash
python manage.py makemigrations
python manage.py migrate

```

### 5. Create a Superuser

Create an admin account to access the dashboard and review portal.

```bash
python manage.py createsuperuser

```

### 6. Run the Development Server

```bash
python manage.py runserver

```

Visit `http://127.0.0.1:8000/` in your browser to view the site.

## 📂 Key Project Structure

```text
spark_project/
│
├── new_spark_website/          # Core Django Settings
│   ├── settings.py
│   └── urls.py
│
├── applications/               # Main App
│   ├── models.py               # Database schemas (Application, Status logic)
│   ├── views.py                # Business logic, CSV/PDF exporters
│   ├── forms.py                # Django ModelForms with custom validation
│   ├── urls.py                 # App routing
│   ├── portal_urls.py          # Dedicated Admin RBAC routing
│   │
│   ├── static/                 # CSS, JS, and Images (Logos/Banners)
│   │   └── images/
│   │
│   └── templates/              # HTML Templates (Bootstrap 5)
│       ├── base.html           # Master layout & Navigation
│       ├── apply.html          # Student application form
│       └── dashboard.html      # Admin review dashboard
│
└── manage.py

```

## 🔒 Managing Roles (RBAC)

To grant a staff member the ability to review applications without giving them full Superuser control:

1. Log in to the default Django admin (`/admin/`).
2. Go to **Groups** and create a group named exactly `Reviewer`.
3. Go to **Users**, select the staff member, and add them to the `Reviewer` group.

## 📄 License

Copyright (c) 2026 Devarakonda Saratchandra Mouli. All rights reserved.

```text
This code and its associated documentation are private property. 
No permission is granted for anyone to copy, modify, merge, publish, 
distribute, sublicense, or sell copies of this software. 

Unauthorized duplication or submission of this work for academic 
or professional credit is strictly prohibited.

```
